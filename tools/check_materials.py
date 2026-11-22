"""Check local navigation, source integrity, and the lecture conversion map.

Uses only Python's standard library. External URLs and factual correctness
require separate review; this check deliberately does not claim to verify them.
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
errors = []


def require(condition, message):
    if not condition:
        errors.append(message)


manifest = json.loads((ROOT / "04_Источники/manifest.json").read_text())
additional = json.loads((ROOT / "04_Источники/additional_manifest.json").read_text())
originals = manifest["files"] + additional["files"]
for item in originals:
    path = ROOT / item["path"]
    require(path.is_file(), f"Missing original: {item['path']}")
    if path.is_file():
        require(hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"],
                f"Changed original: {item['path']}")

materials = json.loads((ROOT / "08_LaTeX/materials.json").read_text())
require(len(materials) == 10, "Expected 10 original PDFs in the conversion map")
require(sum(m["pages"] for m in materials) == 492, "Expected 492 original pages")
require(len({m["id"] for m in materials}) == len(materials), "Duplicate topic IDs")
sources = {i["path"]: i for i in manifest["files"] if i["kind"] == "lecture"}
require({m["source"] for m in materials} == set(sources), "Conversion map must cover every lecture PDF exactly once")
for item in materials:
    require(item["status"] in {"planned", "in_progress", "review", "done"},
            f"Invalid topic status: {item['id']}")
    require((ROOT / item["notes"]).is_file(), f"Missing notes: {item['notes']}")
    require((ROOT / item["source"]).is_file(), f"Missing source: {item['source']}")
    if item["source"] in sources:
        require(item["pages"] == sources[item["source"]]["pdf_pages"], f"Wrong page count: {item['id']}")
    if item["kind"] == "slides" and (ROOT / item["notes"]).is_file():
        count = len(re.findall(r"^## Слайд \d+", (ROOT / item["notes"]).read_text(), re.M))
        require(count == item["pages"], f"Slide headings: {item['id']}: {count} vs {item['pages']}")
    if item["status"] != "planned":
        require((ROOT / item["target"]).is_file(), f"Missing LaTeX source: {item['target']}")

names = subprocess.check_output(
    ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
    cwd=ROOT,
).decode().split("\0")
markdown_count = 0
link_count = 0
for name in sorted(set(filter(None, names))):
    path = ROOT / name
    if path.suffix != ".md" or not path.is_file():
        continue
    markdown_count += 1
    content = path.read_text()
    # Ignore code fences and inline code; commands and example placeholders
    # need not be valid local links.
    content = re.sub(r"^```[^\n]*\n.*?^```[^\n]*$", "", content, flags=re.M | re.S)
    content = re.sub(r"`[^`\n]*`", "", content)
    for match in re.finditer(r"!?\[[^\]\n]*\]\((<[^>]+>|[^\n]*?)\)(?=\s|[.,;:|]|$)", content):
        target = match[1].strip().strip("<>")
        parts = urlsplit(target)
        if parts.scheme or parts.netloc or not parts.path:
            continue
        link_count += 1
        destination = path.parent / unquote(parts.path)
        require(destination.exists(), f"Broken local link in {name}: {target}")
    if name.startswith("05_Конспекты/"):
        require(not re.search(r"\\(?:frac|sqrt|mathrm|quad)\b|\\[\[\]()]",
                              content), f"Raw LaTeX in Markdown notes: {name}")

require(len(list((ROOT / "05_Конспекты").glob("[0-9][0-9]_*.md"))) == 10,
        "Expected one current note per original PDF (10 total)")
require(len(list((ROOT / "06_Практикум/Задания").glob("[0-9][0-9]_*.md"))) == 15,
        "Expected 15 practice assignments")
tasks = json.loads((ROOT / "docs/tasks.json").read_text())
require(len({t["id"] for t in tasks}) == len(tasks), "Duplicate task IDs")

if errors:
    print("FAILED:\n" + "\n".join(f"- {e}" for e in errors))
    sys.exit(1)
print(f"PASS: {len(originals)} original hashes; {len(materials)} topics; "
      f"{markdown_count} Markdown files; {link_count} local links; 15 practices")
