#!/bin/bash
# Regenerate INDEX.md from the queue, the reviews written so far, and the run history.
. /home/ubuntu/charm-review/bin/lib.sh
python3 - <<'PY'
import csv,os,pathlib,datetime,re
root=pathlib.Path("/home/ubuntu/charm-review")
q=list(csv.DictReader(open(root/"queue.tsv"),delimiter="\t"))
cursor=int((root/"state/cursor").read_text().strip()) if (root/"state/cursor").exists() else 1
hist={}
hp=root/"state/history.tsv"
if hp.exists():
    for line in hp.read_text().splitlines():
        p=line.split("\t")
        if len(p)>=6: hist[p[2]]=p
done=[]; pending=[]
for r in q:
    f=root/"reviews"/f"{r['repo']}.md"
    if f.exists() and f.stat().st_size>500:
        h=hist.get(r["repo"],[])
        first=""
        try:
            for ln in f.read_text().splitlines():
                if ln.strip() and not ln.startswith("#") and not ln.startswith("|"):
                    first=ln.strip()[:160]; break
        except Exception: pass
        # Count only the headings inside "## Findings". Counting every "### " in
        # the file swept up the per-deployment subsections of the deployment log
        # too, and reported 38 findings for a review that has 12.
        body=f.read_text()
        m=re.search(r"^## Findings\s*$(.*?)(?=^## |\Z)",body,re.M|re.S)
        nfind=len(re.findall(r"^### ",m.group(1),re.M)) if m else 0
        done.append((r,f,h,first,nfind))
    else: pending.append(r)
out=[]
out.append("# Charm reviews\n")
out.append(f"One charm per run, six runs a day. **{len(done)} of {len(q)} reviewed**, "
           f"next up is #{cursor}"+(f" ({q[cursor-1]['repo']})" if 0<cursor<=len(q) else "")+".\n")
out.append(f"_Regenerated {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}._\n")
out.append("## Reviewed\n")
if done:
    out.append("| # | charm | kind | findings | cost | review |")
    out.append("|---|---|---|---|---|---|")
    for r,f,h,first,nf in done:
        cost=next((x.split("=")[1] for x in h if x.startswith("cost=")),"—")
        out.append(f"| {r['idx']} | {r['repo']} | {r['kind']} | {nf} | {cost} | [md](reviews/{r['repo']}.md) |")
else:
    out.append("_none yet_")
out.append("\n## Queue\n")
out.append("| # | charm | org | kind | last commit |")
out.append("|---|---|---|---|---|")
for r in pending[:40]:
    out.append(f"| {r['idx']} | {r['repo']} | {r['org']} | {r['kind']} | {r['last_commit']} |")
if len(pending)>40: out.append(f"\n_…and {len(pending)-40} more, see `queue.tsv`._")
(root/"INDEX.md").write_text("\n".join(out)+"\n")
print(f"index: {len(done)} reviewed, {len(pending)} pending")
PY
