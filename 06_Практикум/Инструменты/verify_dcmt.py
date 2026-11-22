"""Compare serialized generators with upstream's new_example2 vector."""
import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
VECTORS=[
    [0x527415d6,0x77876c15,0xf09e6dea,0xd582955c,0x3bee0f14,0xbbf15d5e,0xdb6d7f03,0x19fef1a1,0xd95d4add,0x17335683],
    [0x00af2259,0xc7d8a3a7,0x7ec9c866,0x0f3c64ba,0xabbcbd72,0xad5b6275,0xc060150e,0x0e57a0a4,0x2d44a12f,0x62913251],
]
def checksum(values):
    value=1469598103934665603
    for v in values:value=((value^v)*1099511628211)&((1<<64)-1)
    return str(value)

checks=0
def run(name,*args,env=None,bad=False):
    global checks
    r=subprocess.run([str(ROOT/"build"/name),*map(str,args)],text=True,capture_output=True,timeout=120,env=env)
    checks+=1
    if bad:
        assert r.returncode!=0,r.stdout
        return
    assert r.returncode==0,(r.returncode,r.stderr)
    return json.loads(r.stdout.strip().splitlines()[-1])

with tempfile.TemporaryDirectory(prefix="hpc-dcmt-") as directory:
    d=Path(directory);cfg=d/"parameters.txt"
    run("dcmt_seq","create",cfg)
    run("dcmt_seq","create",d/"repeat.txt")
    assert cfg.read_bytes()==(d/"repeat.txt").read_bytes()
    actual=run("dcmt_seq","run",cfg,10)
    assert actual["checksums"]==list(map(checksum,VECTORS)),actual
    reference=run("dcmt_seq","run",cfg,1000)
    for threads in (1,2,4):
        env=dict(os.environ,OMP_NUM_THREADS=str(threads),OMP_DYNAMIC="false",OMP_SCHEDULE="dynamic,1")
        assert run("dcmt_omp","run",cfg,1000,env=env)==reference
    (d/"broken.txt").write_text("DCMT_PARAMS_V1 2\n0 1234\n")
    run("dcmt_seq","run",d/"broken.txt",10,bad=True)
    run("dcmt_seq","run",cfg,0,bad=True)
print(json.dumps({"checks":checks,"status":"passed","oracle":"first two columns of upstream new_example2: IDs 0/1, search seed 4172, initialization seeds 1234/4567"}))
