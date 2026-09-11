#!/bin/bash
# prepare.sh <repo-name> <src-path> <workspace>
# Builds the working copy and gathers everything the reviewer should not have
# to spend agent tokens fetching: git history, charmhub metadata, docs, issues.
. /home/ubuntu/charm-review/bin/lib.sh
set -u

REPO="$1"; SRC="$2"; WS="$3"
mkdir -p "$WS"
CTX="$WS/_context"; mkdir -p "$CTX"

# 1. working copy with history. The cache clones are depth-1; deepen from the
#    real origin so the reviewer can read blame, changelogs and churn. Bounded
#    so a huge repo cannot eat the disk or the clock.
git clone --quiet "$SRC" "$WS/repo" 2>/dev/null || cp -a "$SRC" "$WS/repo"
ORIGIN=$(git -C "$SRC" remote get-url origin 2>/dev/null)
if [ -n "$ORIGIN" ]; then
  git -C "$WS/repo" remote set-url origin "$ORIGIN"
  timeout 420 git -C "$WS/repo" fetch --quiet --depth=400 origin 2>/dev/null &&
    git -C "$WS/repo" log --oneline -400 > "$CTX/git-log.txt" 2>/dev/null
  echo "$ORIGIN" > "$CTX/origin.txt"
fi
# 1b. the charm's declared dependencies, unpacked. A thin-wrapper charm keeps its logic
#     in a PyPI package, so without this both the reviewer and the citation checker are
#     looking at 22 lines of import statements. Best-effort and bounded — never fatal.
timeout 360 python3 "$ROOT/bin/fetch-deps.py" "$WS/repo" "$WS/deps" > "$CTX/deps.txt" 2>&1 ||
  echo "fetch-deps: gave up" >> "$CTX/deps.txt"

git -C "$WS/repo" log -1 --format='%H %cs %an %s' > "$CTX/head.txt" 2>/dev/null
git -C "$WS/repo" shortlog -sn --all 2>/dev/null | head -25 > "$CTX/contributors.txt"

# 2. charm names declared in the repo
python3 - "$WS/repo" > "$CTX/charms.json" 2>/dev/null <<'PY'
import sys,pathlib,json,yaml,re
rd=pathlib.Path(sys.argv[1]); out=[]
skip=re.compile(r"(/\.git/|/\.tox/|/venv/|/\.venv/|site-packages|node_modules)")
for cc in rd.rglob("charmcraft.yaml"):
    if skip.search(str(cc)): continue
    def load(p):
        try:
            d=yaml.safe_load(p.read_text()); return d if isinstance(d,dict) else {}
        except Exception: return {}
    m={**load(cc.parent/"metadata.yaml"),**load(cc)}
    if not m.get("name"): continue
    out.append({"name":m["name"],"dir":str(cc.parent.relative_to(rd)),
                "kind":"k8s" if m.get("containers") else "machine",
                "summary":m.get("summary"),
                "containers":list((m.get("containers") or {}).keys()),
                "provides":list((m.get("provides") or {}).keys()),
                "requires":list((m.get("requires") or {}).keys()),
                "storage":list((m.get("storage") or {}).keys()),
                "resources":list((m.get("resources") or {}).keys())})
json.dump(out,sys.stdout,indent=1)
PY

# 3. charmhub: is it published, on what channels, with what docs
python3 - "$CTX" <<'PY' > "$CTX/charmhub.md" 2>/dev/null
import json,sys,pathlib,urllib.request
ctx=pathlib.Path(sys.argv[1])
try: charms=json.loads((ctx/"charms.json").read_text())
except Exception: charms=[]
F="channel-map,default-release,result.summary,result.description,result.links,result.publisher"
for c in charms:
    n=c["name"]
    print(f"\n## charmhub: {n}\n")
    try:
        u=f"https://api.charmhub.io/v2/charms/info/{n}?fields={F}"
        d=json.load(urllib.request.urlopen(u,timeout=20))
    except Exception as e:
        print(f"not found on charmhub ({e})"); continue
    r=d.get("result",{})
    print("publisher:", (r.get("publisher") or {}).get("display-name"))
    print("summary:", r.get("summary"))
    print("links:", json.dumps(r.get("links") or {}))
    dr=d.get("default-release") or {}
    rev=(dr.get("revision") or {})
    print("default-release:", (dr.get("channel") or {}).get("name"), "rev", rev.get("revision"),
          "bases", json.dumps(rev.get("bases") or rev.get("platforms") or []))
    chans=sorted({(m.get("channel") or {}).get("name") for m in (d.get("channel-map") or [])} - {None})
    print("channels:", ", ".join(chans))
    desc=(r.get("description") or "")[:4000]
    if desc: print("\ndescription:\n", desc)
PY

# 3b. the published documentation. charmhub docs live on discourse; pull the raw
#     markdown of the topic and of anything it navigates to, so the reviewer can
#     compare what the docs promise against what the deployment actually does.
python3 - "$CTX" <<'PY' > "$CTX/published-docs.md" 2>/dev/null
import re,sys,json,pathlib,urllib.request
ctx=pathlib.Path(sys.argv[1])
try: hub=(ctx/"charmhub.md").read_text()
except Exception: sys.exit()
urls=re.findall(r"https://discourse\.charmhub\.io/t/[\w\-]+/(\d+)",hub)
seen=set(); out=[]
def raw(tid):
    try:
        req=urllib.request.Request(f"https://discourse.charmhub.io/raw/{tid}",
                                   headers={"User-Agent":"charm-review/1.0"})
        return urllib.request.urlopen(req,timeout=25).read().decode("utf-8","replace")
    except Exception as e:
        return f"<could not fetch topic {tid}: {e}>"
queue=list(dict.fromkeys(urls))[:2]
while queue and len(seen)<12:
    tid=queue.pop(0)
    if tid in seen: continue
    seen.add(tid)
    body=raw(tid)
    out.append(f"\n\n---\n## discourse topic {tid}\n\n{body[:20000]}")
    for n in re.findall(r"discourse\.charmhub\.io/t/[\w\-]+/(\d+)",body):
        if n not in seen and len(seen)+len(queue)<12: queue.append(n)
print("".join(out) if out else "no published docs found on discourse")
PY

# 4. repo docs worth reading, listed not inlined (the agent opens what it needs)
{
  echo "# Docs present in the repo"
  find "$WS/repo" -maxdepth 3 \( -iname '*.md' -o -iname '*.rst' \) \
       -not -path '*/.git/*' -not -path '*/node_modules/*' -printf '%P\t%s bytes\n' 2>/dev/null | sort | head -60
  echo
  echo "# Test layout"
  find "$WS/repo" -maxdepth 3 -type d \( -name tests -o -name spread -o -name integration -o -name unit -o -name scenario \) \
       -not -path '*/.git/*' -printf '%P\n' 2>/dev/null | head -30
  echo
  echo "# CI workflows"
  ls "$WS/repo/.github/workflows" 2>/dev/null | head -30
  echo
  echo "# Env hints (concierge/spread/tox configs the project itself uses)"
  find "$WS/repo" -maxdepth 2 \( -name 'concierge*.yaml' -o -name 'spread.yaml' -o -name 'tox.ini' -o -name 'justfile' -o -name 'Makefile' \) -printf '%P\n' 2>/dev/null
} > "$CTX/inventory.txt" 2>/dev/null

# 5. open issues + recent releases from GitHub (unauthenticated; best effort)
if [ -n "${ORIGIN:-}" ]; then
  SLUG=$(echo "$ORIGIN" | sed -E 's#.*github.com[:/]##; s#\.git$##')
  case "$ORIGIN" in *github.com*)
    curl -sS --max-time 25 "https://api.github.com/repos/$SLUG/issues?state=open&per_page=40&sort=updated" \
      2>/dev/null | python3 -c "
import json,sys
try: d=json.load(sys.stdin)
except Exception: sys.exit()
if isinstance(d,list):
    for i in d:
        if 'pull_request' in i: continue
        print(f\"#{i['number']} [{i['updated_at'][:10]}] {i['title']}\")
        b=(i.get('body') or '')[:400].replace(chr(10),' ')
        if b: print('   ',b)
" > "$CTX/open-issues.txt" 2>/dev/null ;;
  esac
fi

# 6. environment snapshot so the reviewer knows what it is working with
{
  echo "# Controllers"; juju controllers 2>&1
  echo; echo "# Disk"; df -h / | tail -1
  echo "# Memory"; free -h | head -2
  echo "# CPU"; nproc
} > "$CTX/environment.txt" 2>&1

echo "$WS"
