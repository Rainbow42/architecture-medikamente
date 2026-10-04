from pathlib import Path
import re
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
errors = []
pages = 0
diagrams = sorted(ROOT.glob("Task*/*.drawio"))
previews = sorted(ROOT.glob("Task*/*.svg"))
documents = [ROOT / "README.md", *ROOT.glob("Task*/*.md"), *ROOT.glob("docs/*.md")]

for path in diagrams:
    tree = ET.parse(path)
    assert tree.getroot().tag == "mxfile", path
    for page in tree.findall("diagram"):
        pages += 1
        cells = page.findall(".//mxCell")
        ids = [cell.get("id") for cell in cells]
        if len(ids) != len(set(ids)):
            errors.append(f"{path.name}: duplicate cell ID")
        for cell in cells:
            for attribute in ("parent", "source", "target"):
                if cell.get(attribute) and cell.get(attribute) not in ids:
                    errors.append(f"{path.name}: unresolved {attribute}")
        if not page.findall(".//mxCell[@vertex='1']"):
            errors.append(f"{path.name}: empty diagram")

for path in previews:
    tree = ET.parse(path)
    if tree.getroot().tag != "{http://www.w3.org/2000/svg}svg":
        errors.append(f"{path.name}: invalid SVG root")

for path in documents:
    for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
        if target.startswith(("https://", "http://", "#")):
            continue
        file_target = target.split("#", 1)[0]
        if not (path.parent / file_target).is_file():
            errors.append(f"{path.relative_to(ROOT)}: missing {target}")

for task in range(1, 7):
    if not list((ROOT / f"Task{task}").glob("*.md")):
        errors.append(f"Task{task}: missing explanation")

if pages != len(previews):
    errors.append(f"{pages} diagram pages but {len(previews)} previews")

if errors:
    raise SystemExit("\n".join(errors))
print(f"OK: {len(diagrams)} drawio files, {pages} pages, {len(previews)} SVG previews")
print(f"OK: {len(documents)} Markdown files; local links and Task1–Task6 checked")
