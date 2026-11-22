"""Application checkpoint: version, parameters, state and an integrity digest."""
import argparse
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path

PARAMS = {"coefficient": 0.75, "input": "index_mod_5_minus_2"}


def canonical(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def load(path):
    record = json.loads(Path(path).read_text())
    digest = record.pop("sha256", None)
    if digest != hashlib.sha256(canonical(record)).hexdigest():
        raise ValueError("checkpoint integrity check failed")
    if record.get("version") != 1 or record.get("parameters") != PARAMS:
        raise ValueError("incompatible checkpoint")
    step, value = record.get("completed_steps"), record.get("value")
    if type(step) is not int or step < 0 or type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError("invalid checkpoint state")
    return step, float(value)


def save(path, step, value):
    path = Path(path)
    record = {"version": 1, "parameters": PARAMS, "completed_steps": step, "value": value}
    record["sha256"] = hashlib.sha256(canonical(record)).hexdigest()
    # Same directory is needed for atomic replacement on one filesystem.
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(record, stream, sort_keys=True, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, required=True)
    parser.add_argument("--until", type=int)
    parser.add_argument("--resume", type=Path)
    parser.add_argument("--save", type=Path, required=True)
    args = parser.parse_args()
    try:
        step, value = load(args.resume) if args.resume else (0, 0.0)
        target = args.steps if args.until is None else args.until
        if not 0 <= step <= target <= args.steps <= 10000000:
            raise ValueError("require completed <= until <= steps <= 10000000")
        for i in range(step, target):
            value = 0.75 * value + (i % 5) - 2
        save(args.save, target, value)
        print(json.dumps({"completed_steps": target, "value": value}))
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(2, str(error) + "\n")


if __name__ == "__main__":
    main()
