# Script transcripts — gate witness audit, 2026-09-30

The exact source of the throwaway scripts the delegated audit agents ran, kept as a transcript so the record shows what produced each output file. They are **not** runnable code in this tree: they were written as one-off probes, do not meet the repository's lint, type, complexity or docstring gates, and are deliberately not committed as `.py` files (operator ruling, 2026-10-01: "Scripts as transcript").

One change from what ran: the scripts held absolute paths to the session scratch directory and the maintainer's checkout. Those were replaced, before this record landed, with paths computed from the script's own location (`Path(__file__).resolve().parent` for outputs, `Path(__file__).resolve().parents[3]` for the repository root, and a temporary directory for `build.py`'s rebuild root). Nothing else was edited.

## Used by `auditA.md`

### `a889.py`

```python
import glob
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

R=str(Path(__file__).resolve().parents[3])+'/'
def T(s):
    d=datetime.fromisoformat(s.replace('Z','+00:00')); return d if d.tzinfo else d.replace(tzinfo=UTC)
rows=[]
for i,l in enumerate(open(R+'.gzkit/ledger.jsonl'),1):
    if l.strip():
        e=json.loads(l); e['_ln']=i; rows.append(e)
rec={}
for p in glob.glob(R+'artifacts/receipts/arb-*.json'):
    try: d=json.load(open(p))
    except: continue
    rid=d.get('run_id') or p.split('/')[-1][:-5]
    step='lint' if str(d.get('schema','')).startswith('gzkit.arb.lint_receipt') else (d.get('step') or {}).get('name') if isinstance(d.get('step'),dict) else None
    ts=d.get('timestamp_utc')
    rec[rid]=dict(step=step,ts=T(ts) if ts else None,ex=d.get('exit_status'))
lo,hi=T(sys.argv[1]),T(sys.argv[2])
comps=[e for e in rows if e.get('event')=='obpi_receipt_emitted' and e.get('receipt_event')=='completed' and lo<=T(e['ts'])<hi]
RID=re.compile(r'arb-(?:ruff|step-[a-z][a-z0-9-]*?)-[a-f0-9]{32}')
out=[]
for c in comps:
    ct=T(c['ts']); oid=c['id']; ev=c.get('evidence') or {}
    claims=[T(e['ts']) for e in rows if e.get('event')=='obpi_lock_claimed' and e.get('id')==oid and T(e['ts'])<=ct]
    claim=max(claims) if claims else None
    mb=[e for e in rows if e.get('event')=='audit_receipt_emitted' and e.get('receipt_event')=='meta-receipt-bind' and (e.get('evidence') or {}).get('obpi_id')==oid and 0<= (ct-T(e['ts'])).total_seconds()<3600]
    text=json.dumps(ev)
    cited=sorted(set(RID.findall(text)))
    cst=[]
    for r in cited:
        x=rec.get(r); cst.append((r, None if x is None else x['ex']))
    newest={}
    if claim:
        for rid,x in rec.items():
            if x['step'] in('lint','typecheck','unittest') and x['ts'] and claim<=x['ts']<=ct:
                if x['step'] not in newest or x['ts']>newest[x['step']][0]: newest[x['step']]=(x['ts'],rid,x['ex'])
    lane=ev.get('parent_lane')
    red_cited=[r for r,s in cst if s not in (None,0)]
    missing=[r for r,s in cst if s is None]
    ncomplete=all(s in newest for s in('lint','typecheck','unittest'))
    nred=[(s,v[1],v[2]) for s,v in newest.items() if v[2]!=0]
    if red_cited: cls='EXPLOITED?'
    elif ncomplete and not nred: cls='EXPOSED-CLEAN'
    elif nred: cls='NEWEST-RED'
    else: cls='UNDETERMINABLE'
    out.append(dict(ln=c['_ln'],id=oid,ts=c['ts'][:19],lane=lane,claim=str(claim)[:19] if claim else None,meta=[(m['_ln'],m['evidence'].get('resolved_receipt_ids')) for m in mb],cited=cst,newest={s:(v[1],v[2]) for s,v in newest.items()},cls=cls))
import collections

print(len(out),collections.Counter(o['cls'] for o in out))
json.dump(out,open(sys.argv[3],'w'),indent=1,default=str)
```

### `c1093b.py`

```python
import glob
import json
import re
import subprocess
import tempfile
from pathlib import Path

from gzkit.governance.stage4_evidence import extract_demo_commands

rows=[(i,json.loads(l)) for i,l in enumerate(open('.gzkit/ledger.jsonl'),1) if l.strip()]
comps=[(i,e) for i,e in rows if e.get('event')=='obpi_receipt_emitted' and e.get('receipt_event')=='completed' and '2026-06-24T11:44:11'<=e['ts']<'2026-09-26T00:50:07']
briefs={Path(p).stem:p for p in glob.glob('docs/design/adr/**/obpis/OBPI-*.md',recursive=True)}
W=re.compile(r'\bgz\s+(?:[a-z-]+\s+)*?(commit|remember|retire|attest|complete|sync|emit-receipt|create|claim|release|withdraw|repudiate|land|compose|unown|record|register-adrs|init|closeout|park|block|start|append|git-sync|advise-rendition|migrate|archive)\b|\brm\b|\bmv\b|write_text|write_bytes',re.I)
for i,e in comps:
    oid=e['id']; p=briefs.get(oid) or next((v for k,v in briefs.items() if k.startswith(oid)),None)
    # brief as of the last commit before completion ts
    rev=subprocess.run(['git','rev-list','-1','--before='+e['ts'],'HEAD'],capture_output=True,text=True).stdout.strip()
    txt=None
    if p:
        r=subprocess.run(['git','log','-1','--format=%H','--before='+e['ts'],'--',p],capture_output=True,text=True).stdout.strip()
        # brief may have been renamed; fall back to current
        if r:
            t=subprocess.run(['git','show',f'{r}:{p}'],capture_output=True,text=True)
            if t.returncode==0: txt=t.stdout
        if txt is None: txt=Path(p).read_text()
    if txt is None: print(i,oid,'NO-BRIEF'); continue
    f=tempfile.NamedTemporaryFile('w',suffix='.md',delete=False); f.write(txt); f.close()
    cmds=extract_demo_commands(Path(f.name))
    flag=[c[:220].replace('\n',' ') for c in cmds if W.search(c) and '--help' not in c and '--dry-run' not in c]
    print(i,e['ts'][:19],oid,'demos=%d'%len(cmds),'WRITE?' if flag else '',flag)
```

## Used by `auditC.md`

### `audit1057.py`

```python
"""Read-only replay of pre-fix plan-audit PASS receipts against the fixed containment predicate."""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[3])
SP = Path(sys.argv[0]).parent
sys.path.insert(0, REPO + "/src")
from gzkit.commands.plan_audit_cmd import _extract_plan_paths as new_extract
from gzkit.commands.plan_audit_cmd import _path_within_allowed as new_within
from gzkit.governance.brief_path_validity import extract_allowed_paths

FIX_TS = "2026-09-19T23:23:52"


def git(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True, errors="replace").stdout


def old_extract(content):
    paths = []
    for line in content.splitlines():
        for prefix in ("src/", "tests/", "docs/"):
            if prefix in line:
                for token in line.split():
                    token = token.strip("`").strip("*").strip(",").strip(")")
                    if token.startswith(prefix) or token.startswith(f"./{prefix}"):
                        paths.append(token.lstrip("./"))
    return sorted(set(paths))


def old_within_nofallback(path, allowed):
    for a in allowed:
        c = a.rstrip("/")
        if path == c or path.startswith(c + "/"):
            return True
    return False


entries = []
cur = None
for line in (SP / "receipt_hist.txt").read_text().splitlines():
    if line.startswith("C "):
        _, sha, ts = line.split()
        cur = (sha, ts)
    elif line.strip():
        entries.append((cur[0], cur[1], line.strip()))

seen = {}
for sha, cts, path in entries:
    raw = git("show", f"{sha}:{path}")
    try:
        r = json.loads(raw)
    except Exception:
        continue
    key = (r.get("obpi_id"), r.get("timestamp"))
    if key in seen:
        continue
    seen[key] = (sha, cts, path, r)

rows = []
tmp = Path(tempfile.mkdtemp(dir=SP))
for (obpi, ts), (sha, cts, path, r) in sorted(seen.items(), key=lambda kv: kv[0][1] or ""):
    if not ts or ts[:19] >= FIX_TS:
        continue
    row = {"obpi": obpi, "ts": ts, "commit": sha[:9], "verdict": r.get("verdict"), "plan": r.get("plan_file")}
    rows.append(row)
    if r.get("verdict") != "PASS" or not obpi or not r.get("plan_file"):
        row["status"] = "not-pass-or-no-plan"
        continue
    plan = git("show", f"{sha}:.claude/plans/{r['plan_file']}")
    if not plan:
        row["status"] = "plan-missing-at-commit"
        continue
    m = re.match(r"OBPI-(\d+\.\d+\.\d+-\d+)", obpi)
    short = m.group(0) if m else obpi
    briefs = [p for p in git("ls-tree", "-r", "--name-only", sha, "docs/design/adr").splitlines()
              if "/obpis/" in p and Path(p).name.startswith(short)]
    if not briefs:
        row["status"] = "brief-missing-at-commit"
        continue
    bt = tmp / "brief.md"
    bt.write_text(git("show", f"{sha}:{briefs[0]}"), encoding="utf-8")
    allowed = extract_allowed_paths(bt)
    row["brief"] = briefs[0]
    if allowed is None:
        row["status"] = "no-allowlist"
        continue
    pt = tmp / "plan.md"
    pt.write_text(plan, encoding="utf-8")
    oldp = old_extract(plan)
    newp = new_extract(pt)
    row["old_masked"] = [p for p in oldp if not old_within_nofallback(p, allowed)]
    row["old_out_newpred"] = [p for p in oldp if not new_within(p, allowed)]
    row["new_out"] = [p for p in newp if not new_within(p, allowed)]
    row["allowed"] = allowed
    row["status"] = "checked"

(SP / "audit1057.json").write_text(json.dumps(rows, indent=1))
from collections import Counter

print(Counter(r["status"] if r["status"] != "checked" else ("checked-masked" if r["old_masked"] else "checked-clean") for r in rows))
print("total pre-fix receipts", len(rows), "PASS", sum(r["verdict"] == "PASS" for r in rows))
```

### `touch3.py`

```python
import datetime as dt
import json
import re
import sys
from pathlib import Path

SP=Path(__file__).resolve().parent
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/"src"))
idre=re.compile(r"OBPI-(\d+\.\d+\.\d+-\d+)")
def utc(s): return dt.datetime.fromisoformat(s.replace('Z','+00:00')).astimezone(dt.UTC)
commits=[];cur=None;mode=None
for line in (SP/'commits.txt').read_text(errors='replace').splitlines():
    if line.startswith('@@C '):
        _,sha,ts=line.split(); cur={'sha':sha[:9],'ts':utc(ts),'msg':[],'files':[]}; commits.append(cur); mode='m'
    elif line=='@@F': mode='f'
    elif cur:
        if mode=='m': cur['msg'].append(line)
        elif line.strip(): cur['files'].append(line.strip())
for c in commits: c['ids']={"OBPI-"+i for i in idre.findall("\n".join(c['msg']))}
res=json.load(open(SP/'touch2.json'))
rows=json.load(open(SP/'audit1057.json'))
allowed={}
for r in rows:
    if r.get('status')=='checked' and r['verdict']=='PASS':
        m=idre.search(r['obpi']); allowed["OBPI-"+m.group(1)]=r['allowed']
out=[]
for r in res:
    if not r['completed']:
        r['win']='no-completion'; out.append(r); continue
    a=utc(r['receipt_ts']); b=utc(r['completed'])+dt.timedelta(minutes=30)
    cs=[c for c in commits if a<=c['ts']<=b and (not c['ids'] or r['obpi'] in c['ids'])]
    named=set(r['named_oos'])
    hits={}
    for c in cs:
        for f in c['files']:
            if f in named and f.startswith(('src/','tests/')) :
                hits.setdefault(f,[]).append(c['sha'])
    r['interval_hours']=round((b-a).total_seconds()/3600,1)
    r['named_touched_interval']=hits
    out.append(r)
(SP/'touch3.json').write_text(json.dumps(out,indent=1))
h=[r for r in out if r.get('named_touched_interval')]
print('named&touched(interval):',len(h))
for r in h: print(r['obpi'],r['interval_hours'],{k:v[:3] for k,v in r['named_touched_interval'].items()})
```

### `tier.py`

```python
import json
import re
import subprocess
from pathlib import Path

SP=Path(__file__).resolve().parent
res=[r for r in json.load(open(SP/'touch3.json')) if r.get('named_touched_interval')]
rows=json.load(open(SP/'audit1057.json'))
allowed={};plan={}
idre=re.compile(r"OBPI-(\d+\.\d+\.\d+-\d+)")
for r in rows:
    if r.get('status')=='checked' and r['verdict']=='PASS':
        k="OBPI-"+idre.search(r['obpi']).group(1); allowed[k]=r['allowed']; plan[k]=(r['commit'],r['plan'])
def msg(s): return subprocess.run(['git','log','-1','--format=%s%n%b',s],capture_output=True,text=True).stdout
out=[]
for r in res:
    o=r['obpi']; hits=r['named_touched_interval']
    shas=sorted({s for v in hits.values() for s in v})
    tagged=[s for s in shas if o in msg(s)]
    placeholder=any('<' in a for a in allowed[o])
    nontriv=[f for f in hits if not f.endswith('__init__.py')]
    tier='A' if (tagged or r['interval_hours']<=12) and nontriv and not placeholder else ('B-init-only' if not nontriv else ('B-placeholder' if placeholder else 'B-long-window-untagged'))
    out.append(dict(obpi=o,tier=tier,hours=r['interval_hours'],receipt_ts=r['receipt_ts'][:16],receipt_commit=plan[o][0],plan=plan[o][1],files=sorted(hits),shas=shas,tagged=tagged,completed=r['completed'][:16]))
json.dump(out,open(SP/'tier.json','w'),indent=1)
import collections;print(collections.Counter(x['tier'] for x in out))
for x in out:
    if x['tier']!='A': print(x['tier'],x['obpi'],x['files'][:3])
```

### `red849.py`

```python
import collections
import json
import subprocess
from pathlib import Path

SP=Path(__file__).resolve().parent
A,C="2026-07-09T11:16","2026-09-06T15:37"
ev=[json.loads(l) for l in open('.gzkit/ledger.jsonl')]
red=[e for e in ev if e['event']=='red_receipt_emitted' and A<=e['ts'][:16]<C]
def g(*a): return subprocess.run(['git',*a],capture_output=True,text=True)
intro={}
for req in sorted({e['req_id'] for e in red}):
    out=g('log','-S',f'@covers("{req}")','--format=%H','--reverse','--','tests').stdout.split()
    intro[req]=out[0] if out else None
rows=[]
for e in red:
    i=intro[e['req_id']]; b=e.get('base_commit')
    if i is None: rel='no-intro'
    elif not b: rel='no-base'
    else:
        rel='base-has-test' if g('merge-base','--is-ancestor',i,b).returncode==0 else 'base-lacks-test'
    rows.append(dict(ts=e['ts'][:19],req=e['req_id'],cls=e.get('failure_class'),prov=e.get('base_provenance'),base=(b or '')[:9],intro=(i or '')[:9],rel=rel,id=e['receipt_id']))
json.dump(rows,open(SP/'red849.json','w'),indent=1)
print(collections.Counter((r['rel'],r['cls']) for r in rows))
```

## Used by `auditD.md`

### `build.py`

```python
"""Reconstruct mkdocs dead-link warnings at historical commits, in scratch only.

usage: python3 build.py <commit> [<commit> ...]
Extracts mkdocs.yml + docs/ (+ overrides/config/hooks if present) via git archive,
raises validation.links.not_found ignore -> warn, builds, counts WARNING lines.
Never touches the repo working tree.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[3]
S = Path(__import__("tempfile").mkdtemp(prefix="gzkit-docs-rebuild-"))
MK = R / ".venv/bin/mkdocs"


def extract(commit: str, dest: Path) -> None:
    for p in ["mkdocs.yml", "docs", "overrides", "config", "hooks"]:
        a = subprocess.run(["git", "-C", str(R), "archive", commit, p], capture_output=True)
        if a.returncode == 0:
            subprocess.run(["tar", "-x", "-C", str(dest)], input=a.stdout, check=True)


def build(commit: str) -> str:
    d = S / commit
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    extract(commit, d)
    y = d / "mkdocs.yml"
    s = y.read_text()
    raised = re.subn(r"(\n\s+not_found:\s*)ignore", r"\1warn", s)
    y.write_text(raised[0])
    p = subprocess.run([str(MK), "build", "-f", str(y), "-d", str(d / "site")], cwd=d, capture_output=True, text=True)
    log = p.stdout + p.stderr
    (d / "log.txt").write_text(log)
    warn = [l for l in log.splitlines() if l.startswith("WARNING")]
    link = [l for l in warn if "contains a link" in l or "not found among" in l]
    shutil.rmtree(d / "site", ignore_errors=True)
    return f"{commit} rc={p.returncode} raised={raised[1]} warnings={len(warn)} linkwarn={len(link)}"


if __name__ == "__main__":
    for c in sys.argv[1:]:
        print(build(c), flush=True)
```
