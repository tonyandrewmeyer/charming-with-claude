#!/usr/bin/env python3
"""Destroy this harness's juju models (rv-*) without ever blocking on them.

Two hard-won facts drive the design:

  * `juju destroy-model --force --no-wait` does NOT return promptly. It waits
    until the model is actually gone. A k8s model takes 7-15 minutes, and a
    model whose undertaker worker has died never finishes at all. Blocking on
    it burned ~40 minutes of a 3h cron slot on 2026-07-25.
  * Re-issuing destroy against a model that is already `destroying` blocks
    forever too, so a stuck model poisons every later cleanup.

So: fire the destroy off detached and move on, remember which models we have
seen destroying and for how long, and rip the underlying k8s namespace out by
hand once one has clearly wedged.

A third fact, learned 2026-08-27: everything above enumerates juju *models*, so a
namespace whose model has already gone is invisible to it however it is named.
`rv-identity-saml-provider` sat Active for 11 days holding a pod that way, left by
idx 79's three killed attempts. The orphan sweep at the bottom closes that by
working from the *cluster* side instead — list namespaces, subtract everything
juju knows about, delete what is left. It is the one part of this script that can
delete something juju never told us about, so it abstains rather than guesses:
see the four guards on sweep_orphans().

Prints one plain line per action; cleanup.sh wraps them in its own log format.
"""
import calendar
import json
import os
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(os.environ.get("ROOT", "/home/ubuntu/charm-review"))
STATE = ROOT / "state" / "destroying.tsv"
LOGDIR = ROOT / "logs" / "_destroy"
# A model still destroying after this long is not slow, it is wedged.
REAP_AFTER = int(os.environ.get("REAP_AFTER", "1800"))
# DRY_RUN=1 reports what it would do without touching anything, so this can be
# exercised safely while a review is mid-flight.
DRY_RUN = os.environ.get("DRY_RUN") == "1"
# A namespace younger than this is never swept, however orphaned it looks: juju
# creates the namespace and the model doc at slightly different moments, and the
# sweep must not win that race against a model being born.
ORPHAN_AFTER = int(os.environ.get("ORPHAN_AFTER", "3600"))
CONTROLLERS = [
    c
    for c in (
        os.environ.get("CTL_K8S4", "concierge-k8s-4"),
        os.environ.get("CTL_K8S3", "concierge-k8s-3"),
        os.environ.get("CTL_LXD3", "concierge-lxd"),
        os.environ.get("CTL_LXD4", "concierge-lxd-4"),
    )
    if c
]
# Only these two back the kubernetes cluster, so only these two can vouch for a
# namespace. An LXD controller failing to answer says nothing either way.
K8S_CONTROLLERS = {
    c
    for c in (
        os.environ.get("CTL_K8S4", "concierge-k8s-4"),
        os.environ.get("CTL_K8S3", "concierge-k8s-3"),
    )
    if c
}
ORPHAN_STATE = ROOT / "state" / "orphan-ns.tsv"

out = []


def say(msg):
    out.append(msg)
    print(msg, flush=True)


def juju_json(args, timeout=60):
    try:
        p = subprocess.run(
            ["juju", *args, "--format", "json"],
            capture_output=True, text=True, timeout=timeout,
        )
        return json.loads(p.stdout) if p.returncode == 0 and p.stdout.strip() else None
    except Exception:
        return None


def load_state():
    st = {}
    if STATE.exists():
        for line in STATE.read_text().splitlines():
            parts = line.split("\t")
            if len(parts) == 3:
                st[parts[0]] = {"first": float(parts[1]), "reaped": parts[2] == "1"}
    return st


def save_state(st):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(
        "".join(f"{k}\t{v['first']:.0f}\t{1 if v['reaped'] else 0}\n" for k, v in sorted(st.items()))
    )


def destroy_detached(ctl, name):
    """Fire and forget. The CLI waits for teardown however we ask it not to."""
    if DRY_RUN:
        return
    LOGDIR.mkdir(parents=True, exist_ok=True)
    log = open(LOGDIR / f"{ctl}-{name}.log", "ab")
    subprocess.Popen(
        ["timeout", "3600", "juju", "destroy-model", f"{ctl}:{name}",
         "--force", "--no-wait", "--no-prompt", "--destroy-storage"],
        stdin=subprocess.DEVNULL, stdout=log, stderr=log,
        start_new_session=True,
    )


def reap_k8s(name):
    """Delete the model's kubernetes namespace directly.

    Juju's own model doc stays wedged, which is cosmetic; the pods, PVCs and
    memory they hold are what actually matter to the next run.
    """
    p = subprocess.run(["kubectl", "get", "ns", name], capture_output=True, text=True, timeout=60)
    if p.returncode != 0:
        return False
    if DRY_RUN:
        return True
    subprocess.Popen(
        ["kubectl", "delete", "ns", name, "--wait=false", "--ignore-not-found"],
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    return True


def load_orphans():
    st = {}
    if ORPHAN_STATE.exists():
        for line in ORPHAN_STATE.read_text().splitlines():
            parts = line.split("\t")
            if len(parts) == 3:
                st[parts[0]] = {"first": float(parts[1]), "reaped": parts[2] == "1"}
    return st


def save_orphans(st):
    ORPHAN_STATE.parent.mkdir(parents=True, exist_ok=True)
    ORPHAN_STATE.write_text(
        "".join(f"{k}\t{v['first']:.0f}\t{1 if v['reaped'] else 0}\n" for k, v in sorted(st.items()))
    )


def list_namespaces():
    """[(name, created_epoch)] for every namespace, or None if we could not ask.

    None and [] must stay distinguishable: [] would mean "nothing on the cluster",
    which for this sweep reads as "everything juju knows about is orphaned".
    """
    try:
        p = subprocess.run(
            ["kubectl", "get", "ns", "-o", "json"],
            capture_output=True, text=True, timeout=60,
        )
        if p.returncode != 0 or not p.stdout.strip():
            return None
        items = json.loads(p.stdout).get("items", [])
    except Exception:
        return None
    found = []
    for it in items:
        md = it.get("metadata", {})
        name = md.get("name", "")
        ts = md.get("creationTimestamp", "")
        try:
            born = calendar.timegm(time.strptime(ts, "%Y-%m-%dT%H:%M:%SZ"))
        except Exception:
            born = None
        found.append((name, born))
    return found


def sweep_orphans(known, k8s_ok, now):
    """Delete rv-* namespaces that no juju model on either k8s controller claims.

    Four guards, and every one of them is there because the failure it prevents
    would delete a live review's namespace mid-run:

      1. Both k8s controllers must have answered. An unreachable controller
         returns an empty model list, and an empty list makes every namespace
         look orphaned — the exact shape that made the 08-12 substrate fault
         invisible, pointed the other way.
      2. kubectl must have answered too, distinguishing "no namespaces" from
         "could not ask".
      3. rv-* only. Anything the harness did not create - kubeflow, controller-*,
         kube-system, the operator's own work - is never a candidate.
      4. Old enough, and seen orphaned on an *earlier* run. One bad read of the
         model list can then never be enough on its own.
    """
    if not k8s_ok:
        say("orphan sweep: a k8s controller did not answer, not sweeping this round")
        return
    found = list_namespaces()
    if found is None:
        say("orphan sweep: cannot list namespaces, not sweeping this round")
        return
    st = load_orphans()
    seen = set()
    for name, born in found:
        if not name.startswith("rv-") or name in known:
            continue
        if born is None or now - born < ORPHAN_AFTER:
            continue
        seen.add(name)
        rec = st.get(name)
        if rec is None:
            st[name] = {"first": now, "reaped": False}
            say(f"orphan sweep: {name} has no juju model on either k8s controller — watching it")
            continue
        if rec["reaped"]:
            continue
        age_h = (now - born) / 3600
        if reap_k8s(name):
            say(f"orphan sweep: deleted orphaned namespace {name} ({age_h:.0f}h old, no juju model)")
        else:
            say(f"orphan sweep: {name} went away on its own, nothing to delete")
        rec["reaped"] = True
    for name in [k for k in st if k not in seen]:
        del st[name]
    if not DRY_RUN:
        save_orphans(st)


def main():
    st = load_state()
    now = time.time()
    seen = set()
    # A namespace name is only safe to delete if no controller still has a live
    # model using it — both k8s controllers share one cluster.
    live = set()
    per_ctl = {}
    # Every model name a k8s controller knows about, at any status and whatever it
    # is called. The orphan sweep subtracts this from the cluster's namespaces, so
    # it must NOT be narrowed to rv-* the way the destroy loop below is.
    known_ns = set()
    k8s_ok = bool(K8S_CONTROLLERS)

    for ctl in CONTROLLERS:
        d = juju_json(["models", "-c", ctl])
        if d is None:
            say(f"could not list models on {ctl}, skipping it this round")
            per_ctl[ctl] = None
            if ctl in K8S_CONTROLLERS:
                k8s_ok = False
            continue
        models = []
        for m in d.get("models", []):
            name = m.get("short-name") or m.get("name", "").split("/")[-1]
            if ctl in K8S_CONTROLLERS:
                known_ns.add(name)
            if not name.startswith("rv-"):
                continue
            status = (m.get("status") or {}).get("current", "")
            models.append((name, status))
            if status != "destroying":
                live.add(name)
        per_ctl[ctl] = models

    for ctl in CONTROLLERS:
        models = per_ctl.get(ctl)
        if models is None:
            # Keep this controller's state entries; we simply learned nothing.
            seen.update(k for k in st if k.startswith(f"{ctl}:"))
            continue
        for name, status in models:
            key = f"{ctl}:{name}"
            seen.add(key)
            if status == "destroying":
                rec = st.setdefault(key, {"first": now, "reaped": False})
                age = now - rec["first"]
                if age >= REAP_AFTER and not rec["reaped"]:
                    if name in live:
                        say(f"{key} wedged for {age/60:.0f}m but the name is live elsewhere, not reaping")
                        continue
                    if reap_k8s(name):
                        rec["reaped"] = True
                        say(f"{key} wedged for {age/60:.0f}m — deleted its kubernetes namespace")
                    else:
                        rec["reaped"] = True
                        say(f"{key} wedged for {age/60:.0f}m, nothing left to reclaim")
            else:
                say(f"destroying {key} (detached)")
                destroy_detached(ctl, name)
                st[key] = {"first": now, "reaped": False}
                seen.add(key)

    # Namespaces the loop above cannot see, because their model is already gone.
    sweep_orphans(known_ns, k8s_ok, now)

    # Forget models that have finally gone away.
    for key in [k for k in st if k not in seen]:
        del st[key]

    pending = len(st)
    if pending:
        say(f"{pending} model(s) still tearing down in the background")
    # Only an *unreaped* wedge is worth shouting about: that one may still be holding pods,
    # PVCs and memory the next run needs. Once reap_k8s has taken the namespace out there is
    # nothing left to reclaim and juju's model doc can sit in `destroying` forever at no
    # cost — the module docstring calls that cosmetic, and it is. Counting reaped models as
    # wedged had this warning firing on every single cleanup for the 12 days after
    # rv-forgejo-k8s-v3 was reaped on 2026-08-20: twice a run, several hundred times, always
    # about a model with no resources behind it. That is how a warning stops being one.
    # Report the reaped leftovers separately, and without the WARNING.
    wedged = sum(1 for v in st.values() if now - v["first"] >= REAP_AFTER and not v["reaped"])
    if wedged:
        say(f"WARNING: {wedged} model(s) stuck in destroying — juju's undertaker is not reaping them")
    cosmetic = sum(1 for v in st.values() if v["reaped"])
    if cosmetic:
        say(f"{cosmetic} model doc(s) wedged in destroying, resources already reclaimed")
    if not DRY_RUN:
        save_state(st)
    return 0


if __name__ == "__main__":
    sys.exit(main())
