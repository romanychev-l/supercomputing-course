"""Optional plotting helper; requires matplotlib, unlike verification scripts."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

p=argparse.ArgumentParser()
p.add_argument("summary",type=Path)
args=p.parse_args()
data=json.loads(args.summary.read_text())
rows=data["results"];threads=[r["threads"] for r in rows]
fig,axes=plt.subplots(1,2,figsize=(9,3.8),layout="constrained")
times=[r["median_seconds"]*1000 for r in rows]
low=[(r["median_seconds"]-r["min_seconds"])*1000 for r in rows]
high=[(r["max_seconds"]-r["median_seconds"])*1000 for r in rows]
axes[0].errorbar(threads,times,yerr=[low,high],marker="o",capsize=4,label="OpenMP: median, min/max")
axes[0].axhline(data["seq_seconds"]*1000,color="0.5",ls="--",label="Sequential baseline")
axes[0].set(xlabel="OpenMP threads",ylabel="Kernel wall time (ms)",xticks=threads)
axes[1].plot(threads,[r["speedup_vs_seq"] for r in rows],"o-",label="Speedup vs sequential")
axes[1].plot(threads,[r["speedup_vs_omp1"] for r in rows],"s-",label="Speedup vs OpenMP 1")
axes[1].plot(threads,threads,"--",color="0.6",label="Ideal relative to OpenMP 1")
axes[1].set(xlabel="OpenMP threads",ylabel="Speedup",xticks=threads,ylim=(0,None))
for ax in axes:ax.grid(alpha=.25);ax.legend(fontsize=8)
fig.suptitle(f"Local demonstration: {data['mode']}, N={data['n']:,}; repeats: {data.get('repeats','see CSV')}",fontsize=11)
base=args.summary.with_suffix("")
fig.savefig(base.with_suffix(".png"),dpi=180)
fig.savefig(base.with_suffix(".svg"))
