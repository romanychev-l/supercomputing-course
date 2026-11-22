"""Save raw repeated wall times and two explicitly different speedups."""
import argparse
import csv
import json
import os
import statistics
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument("--mode",choices=("sum","dot","pi","matvec","tri","maxmin"),default="pi")
p.add_argument("--n",type=int,default=1000000)
p.add_argument("--threads",type=int,nargs="+",default=[1,2,4])
p.add_argument("--repeats",type=int,default=5)
p.add_argument("--out",type=Path,default=ROOT/"Результаты"/"timings.csv")
args=p.parse_args()
if args.repeats<3 or any(t<1 for t in args.threads) or 1 not in args.threads:p.error("need >=3 repeats, positive threads including 1")
rows=[]
for variant,threads in [("seq",1)]+[("omp",t) for t in args.threads]:
    env=dict(os.environ,OMP_NUM_THREADS=str(threads),OMP_DYNAMIC="false",OMP_SCHEDULE="static")
    cmd=[str(ROOT/"build"/f"kernels_{variant}"),args.mode,str(args.n)]
    def sample():
        r=subprocess.run(cmd,capture_output=True,text=True,check=True,env=env,timeout=120)
        value=json.loads(r.stdout)
        if value["threads"]!=threads:raise RuntimeError("requested thread count not realized")
        return value
    sample()  # external warm-up; each process also establishes its team before timing
    for repeat in range(args.repeats):
        value=sample()
        if rows and abs(value["value"]-rows[0]["value"])>1e-10*max(1,abs(rows[0]["value"])):raise RuntimeError("results disagree")
        rows.append(dict(variant=variant,threads=threads,repeat=repeat+1,mode=args.mode,n=args.n,seconds=value["seconds"],value=value["value"]))
args.out.parent.mkdir(parents=True,exist_ok=True)
with args.out.open("w",newline="") as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
base=statistics.median(r["seconds"] for r in rows if r["variant"]=="seq")
one=statistics.median(r["seconds"] for r in rows if r["variant"]=="omp" and r["threads"]==1)
summary=[]
for threads in args.threads:
    samples=[r["seconds"] for r in rows if r["variant"]=="omp" and r["threads"]==threads]
    median=statistics.median(samples)
    summary.append(dict(threads=threads,median_seconds=median,min_seconds=min(samples),max_seconds=max(samples),speedup_vs_seq=base/median,speedup_vs_omp1=one/median,efficiency_vs_omp1=one/median/threads))
args.out.with_suffix(".summary.json").write_text(json.dumps({"mode":args.mode,"n":args.n,"repeats":args.repeats,"seq_seconds":base,"omp1_seconds":one,"results":summary},indent=2)+"\n")
print(args.out)
