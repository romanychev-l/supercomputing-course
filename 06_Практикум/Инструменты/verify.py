"""Contract tests for supplied or student binaries; requires Python stdlib only."""
import argparse
import json
import math
import os
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--bin-dir", type=Path, default=ROOT / "build")
parser.add_argument("--serial-only", action="store_true", help="explicitly skip OpenMP and MPI")
parser.add_argument("--mpiexec", default=os.environ.get("MPIEXEC", "mpiexec"))
args = parser.parse_args()
checks = 0


def run(command, env=None, bad=False):
    global checks
    result = subprocess.run(list(map(str, command)), text=True, capture_output=True, env=env, timeout=40)
    checks += 1
    if bad:
        assert result.returncode != 0, (command, "invalid input accepted")
        return None
    assert result.returncode == 0, (command, result.returncode, result.stderr)
    lines = result.stdout.strip().splitlines()
    assert lines, (command, "empty output")
    return json.loads(lines[-1])


def close(a, b, tolerance=1e-10):
    assert math.isfinite(a) and abs(a-b) <= tolerance * max(1.0, abs(b)), (a,b)


def oracle(mode, n):
    if mode == "sum":
        rem = n % 97
        return rem*(rem-1)//2 - 48*rem  # each full period sums to zero
    if mode == "dot":
        return sum((i+1)*((i%7)-3) for i in range(n))
    if mode == "pi":
        return math.fsum(4/(1+((i+0.5)/n)**2) for i in range(n))/n
    if mode == "matvec":
        return (n+1)*n*(n+1)/2
    if mode == "tri":
        return sum(((i+j)%17)-8 for i in range(n) for j in range(i,n))
    return max(min(((17*i+13*j)%101)-50 for j in range(n)) for i in range(n))


for mode in ("sum","dot","pi","matvec","tri","maxmin"):
    for n in (1,3,101):
        ref = oracle(mode,n)
        close(run([args.bin_dir/"kernels_seq",mode,n])["value"],ref)
        if not args.serial_only:
            for threads in (1,2,4):
                env = dict(os.environ, OMP_NUM_THREADS=str(threads), OMP_DYNAMIC="false", OMP_SCHEDULE="dynamic,2")
                value = run([args.bin_dir/"kernels_omp",mode,n],env)
                assert value["threads"] == threads, value
                close(value["value"],ref)
for invalid in ("0","-1","abc","10000001"):
    run([args.bin_dir/"kernels_seq","sum",invalid],bad=True)
run([args.bin_dir/"kernels_seq","unknown",10],bad=True)
for n in (1,1024,2051):
    value=run([args.bin_dir/"mt_seq",n])["checksum"]
    if not args.serial_only:
        for threads in (1,2,4):
            env=dict(os.environ,OMP_NUM_THREADS=str(threads),OMP_DYNAMIC="false",OMP_SCHEDULE="dynamic,1")
            actual=run([args.bin_dir/"mt_omp",n],env)
            assert actual["threads"]==threads and actual["checksum"]==value,actual

reference = ROOT / "Преподавателю" / "Эталоны"
for mode in ("fft","ar"):
    for n in (1,2,8,32):
        result=run([sys.executable,reference/"applied.py",mode,n])
        assert result["max_error"]<1e-9,result
ma=run([sys.executable,reference/"applied.py","ma",4])["values"]
for a,b in zip(ma,[-1,-1.1,-0.7,0.3]):close(a,b)
run([sys.executable,reference/"applied.py","fft",3],bad=True)

with tempfile.TemporaryDirectory(prefix="hpc-check-") as directory:
    d=Path(directory);script=reference/"checkpoint.py"
    full=run([sys.executable,script,"--steps",100,"--save",d/"full.json"])
    for stop in (0,1,17,99,100):
        run([sys.executable,script,"--steps",100,"--until",stop,"--save",d/"part.json"])
        resumed=run([sys.executable,script,"--steps",100,"--resume",d/"part.json","--save",d/"end.json"])
        assert full==resumed,(stop,full,resumed)
    record=json.loads((d/"part.json").read_text());record["value"]+=1
    (d/"damaged.json").write_text(json.dumps(record))
    run([sys.executable,script,"--steps",100,"--resume",d/"damaged.json","--save",d/"unused.json"],bad=True)

if not args.serial_only:
    launcher=shlex.split(args.mpiexec)
    for p in (1,2,3,4):
        for mode in ("sum","pi"):
            for n in (1,17,101):
                result=run([*launcher,"-n",p,args.bin_dir/"mpi_sum_pi",mode,n])
                assert result["processes"]==p,result
                close(result["value"],oracle(mode,n))
        assert run([*launcher,"-n",p,args.bin_dir/"mpi_layout"])["ok"]
        n=11;values=[float(i+1) for i in range(n)]
        for steps in (1,7):
            expected=values[:]
            for _ in range(steps):
                padded=[0.0]+expected+[0.0]
                expected=[.25*padded[i]+.5*padded[i+1]+.25*padded[i+2] for i in range(n)]
            result=run([*launcher,"-n",p,args.bin_dir/"mpi_halo",n,steps])
            assert len(result["values"])==n,result
            for a,b in zip(result["values"],expected):close(a,b)
    run([*launcher,"-n",3,args.bin_dir/"mpi_halo",2,1],bad=True)
    run([*launcher,"-n",2,args.bin_dir/"mpi_sum_pi","sum",0],bad=True)

print(json.dumps({"checks":checks,"status":"passed","scope":"serial_only" if args.serial_only else "serial_openmp_mpi", "note":"applied Python checks validate supplied references, not student parallel implementations"}))
