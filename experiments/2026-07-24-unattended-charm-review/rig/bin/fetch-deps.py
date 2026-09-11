#!/usr/bin/env python3
"""Fetch the charm-logic packages a repo depends on, so citations into them can be checked.

Canonical's data-platform charms have moved to the "single kernel" pattern: the repo is a
thin wrapper (opensearch-dashboards' kubernetes/src/charm.py is 22 lines) and the code
worth reviewing lives in a PyPI distribution — `opensearch-dashboards-charms-single-kernel`
providing `single_kernel_opensearch_dashboards`. verify-citations.py indexed only the
checkout, so every citation into the real code read as "no such file in the repo":
opensearch-dashboards scored `citations checked: 0, problems: 9` on 2026-08-02 with all
nine citations correct. The gate contributed nothing and the two correction passes were
spent re-deriving line numbers the checker should have confirmed.

So fetch the declared direct dependencies and unpack them next to the checkout. Bounded
hard — this runs unattended inside a slot's time budget, and a dependency fetch that hangs
or fills the disk would cost a review:

  * direct dependencies only (`--no-deps`), never the transitive closure
  * wheels preferred; sdists are accepted but nothing is built or executed
  * per-package and overall timeouts, a package-count cap and a byte cap
  * every failure is non-fatal — a partial dep tree still verifies more than none

Usage: fetch-deps.py <repo-root> <out-dir>
Prints one summary line. Always exits 0: this is best-effort enrichment, never a gate.
"""
import re
import shutil
import subprocess
import sys
import pathlib
import tarfile
import tempfile
import time
import zipfile

MAX_PKGS = 25          # direct deps are few; a repo listing more is not a charm
MAX_BYTES = 200 << 20  # 200MB unpacked, well under the headroom cleanup keeps free
PKG_TIMEOUT = 90       # seconds per package
TOTAL_TIMEOUT = 300    # seconds for the whole fetch

SKIP_DIRS = re.compile(r"(^|/)(\.git|\.tox|venv|\.venv|node_modules|site-packages|docs)(/|$)")
# Requirement line -> distribution name. Drops markers, extras, version specifiers.
REQ_NAME = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")
# Not dependencies: poetry states the interpreter here, and these never hold charm logic.
NOT_A_DEP = {"python", "pip", "setuptools", "wheel", "poetry", "poetry-core"}


def dep_specs(repo):
    """Direct dependencies declared anywhere in the repo, as pip-installable specs."""
    specs = {}

    def add(name, spec):
        name = name.lower().replace("_", "-")
        if name in NOT_A_DEP or name in specs:
            return
        specs[name] = spec

    for p in repo.rglob("pyproject.toml"):
        if SKIP_DIRS.search(str(p.relative_to(repo))):
            continue
        try:
            import tomllib

            data = tomllib.loads(p.read_text(errors="replace"))
        except Exception:
            continue
        # PEP 621
        for req in data.get("project", {}).get("dependencies", []) or []:
            m = REQ_NAME.match(str(req))
            if m:
                add(m.group(1), str(req))
        # poetry
        poetry = data.get("tool", {}).get("poetry", {})
        for name, con in (poetry.get("dependencies", {}) or {}).items():
            if isinstance(con, str) and re.fullmatch(r"[\d.]+", con.strip()):
                add(name, f"{name}=={con.strip()}")  # poetry's bare "0.0.8" means ==
            else:
                add(name, name)

    for p in repo.rglob("requirements*.txt"):
        if SKIP_DIRS.search(str(p.relative_to(repo))):
            continue
        try:
            lines = p.read_text(errors="replace").splitlines()
        except Exception:
            continue
        for line in lines:
            line = line.split("#")[0].strip()
            # -e/-r/URLs pull in things we cannot name; skip rather than guess
            if not line or line.startswith("-") or "://" in line:
                continue
            m = REQ_NAME.match(line)
            if m:
                add(m.group(1), line)

    return specs


def unpack(archive, dest):
    """Extract top-level importable packages. Never executes anything from the archive."""
    tmp = pathlib.Path(tempfile.mkdtemp(dir=dest.parent))
    try:
        if archive.suffix == ".whl" or archive.suffix == ".zip":
            with zipfile.ZipFile(archive) as z:
                z.extractall(tmp)
        else:
            with tarfile.open(archive) as t:
                # filter="data" refuses absolute paths, .., symlinks out of tree (3.12)
                t.extractall(tmp, filter="data")
        # an sdist wraps everything in <name>-<version>/; a wheel does not
        roots = [p for p in tmp.iterdir() if p.is_dir()]
        if len(roots) == 1 and not (roots[0] / "__init__.py").exists():
            inner = roots[0]
            src = inner / "src"
            if src.is_dir():
                inner = src
        else:
            inner = tmp
        moved = 0
        for item in inner.iterdir():
            if item.name.endswith((".dist-info", ".egg-info", ".data")):
                continue
            target = dest / item.name
            if target.exists():
                continue
            shutil.move(str(item), str(target))
            moved += 1
        return moved
    except Exception:
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def tree_bytes(path):
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def main() -> int:
    repo, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    if not repo.is_dir():
        print("fetch-deps: no repo")
        return 0
    out.mkdir(parents=True, exist_ok=True)

    specs = dep_specs(repo)
    if not specs:
        print("fetch-deps: no declared dependencies")
        return 0
    if len(specs) > MAX_PKGS:
        print(f"fetch-deps: {len(specs)} deps declared, capped to {MAX_PKGS}")
        specs = dict(list(specs.items())[:MAX_PKGS])

    ok, failed = [], []
    deadline = TOTAL_TIMEOUT
    with tempfile.TemporaryDirectory() as dl:
        for name, spec in specs.items():
            if deadline <= 0:
                failed.append(f"{name}(no time)")
                continue
            if tree_bytes(out) > MAX_BYTES:
                failed.append(f"{name}(size cap)")
                continue
            budget = min(PKG_TIMEOUT, deadline)
            started = time.monotonic()
            # Wheels first, and for a pure-python charm library that is the whole story
            # (both single-kernel packages ship py3-none-any). It matters beyond speed:
            # resolving an sdist makes pip run the project's build backend, and this
            # fetch is unattended. Fall back to an sdist only if there is no wheel at
            # all — the source is the point, and it is a dependency the charm already
            # builds and this run is about to deploy.
            r = None
            for extra in (["--only-binary", ":all:"], []):
                left = budget - (time.monotonic() - started)
                if left <= 1:
                    break
                try:
                    r = subprocess.run(
                        [sys.executable, "-m", "pip", "download", "--no-deps",
                         "--disable-pip-version-check", "--no-input",
                         # pip's default 5 retries with backoff turns an index outage
                         # into minutes per package; this is enrichment, so give up early
                         "--retries", "2", "--timeout", "15",
                         *extra, "-d", dl, spec],
                        capture_output=True, text=True, timeout=left,
                    )
                except subprocess.TimeoutExpired:
                    r = None
                    continue
                if r.returncode == 0:
                    break
            if r is None:
                deadline -= time.monotonic() - started
                failed.append(f"{name}(timeout)")
                continue
            # charge what the fetch actually took, not what it was allowed: charging the
            # allowance spent the whole 300s on the first few packages and starved the
            # rest, which on mongodb-k8s dropped `mongo-charms-single-kernel` — the one
            # package the review's citations were in.
            deadline -= time.monotonic() - started
            if r.returncode != 0:
                failed.append(name)
                continue
            got = False
            for f in sorted(pathlib.Path(dl).iterdir()):
                if f.is_file() and unpack(f, out):
                    got = True
                f.unlink(missing_ok=True)
            (ok if got else failed).append(name)

    tops = sorted(p.name for p in out.iterdir() if p.is_dir())
    print(f"fetch-deps: {len(ok)} of {len(specs)} packages, "
          f"{tree_bytes(out) >> 20}MB, top-level: {', '.join(tops[:12]) or 'none'}")
    if failed:
        print(f"fetch-deps: not fetched: {', '.join(sorted(failed))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
