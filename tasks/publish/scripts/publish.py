"""Copy the paper's inputs into paper/generated/ and check that the documents can find every file they cite.

`paper/generated_manifest.csv` lists, for each figure or table the paper uses, the task output it comes from
(`source`, "<task>/<file>" under OUTPUT_ROOT/tasks/) and its name under `paper/generated/` (`generated_path`).
This script
  - copies each source into `paper/generated/` (and fails if a source is missing, or two rows share a name);
  - warns about files in `paper/generated/` that the manifest does not list;
  - checks that every uncommented `\\includegraphics` and `\\input` in the documents (every .tex file in
    `paper/` and `paper/slides/`) resolves, and fails if one does not, so a missing file is caught before LaTeX runs;
  - reports which files are new or changed (by SHA-256);
  - if SHARED_OUTPUT_ROOT is set, mirrors `paper/generated/` into SHARED_OUTPUT_ROOT/generated/ for coauthors.

`paper/generated/figures/` is not tracked by git (no images are); `paper/generated/tables/` is, so `git diff`
shows which numbers moved after a rebuild. Compile the documents afterwards with latexmk in `paper/`.
"""

import csv
import hashlib
import re
import shutil
import sys
from pathlib import Path

from project_package.config import SHARED_OUTPUT_ROOT, TASK_OUTPUT_ROOT
from project_package.paths import REPO_ROOT

PAPER = REPO_ROOT / "paper"
GENERATED = PAPER / "generated"
MANIFEST = PAPER / "generated_manifest.csv"
GRAPHICS_EXTENSIONS = ["", ".png", ".jpg", ".jpeg", ".pdf"]


def documents() -> list[Path]:
    """Return the documents whose references must resolve: every .tex file in paper/ and paper/slides/."""
    return sorted(PAPER.glob("*.tex")) + sorted(PAPER.glob("slides/*.tex"))


def sha256(path: Path) -> str:
    """Return the SHA-256 hash of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def tex_commands(path: Path) -> list[tuple[str, str]]:
    """Return (command, argument) for each uncommented includegraphics, input and graphicspath in a .tex file."""
    pattern = re.compile(r"\\(includegraphics|input|graphicspath)\s*(?:\[[^\]]*\])?\s*\{((?:[^{}]|\{[^{}]*\})*)\}")
    commands = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        code = re.split(r"(?<!\\)%", line)[0]  # drop LaTeX comments
        commands += [(m.group(1), m.group(2)) for m in pattern.finditer(code)]
    return commands


def read_manifest() -> list[dict]:
    """Read the manifest and check that no two rows map to the same generated file."""
    with open(MANIFEST, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    targets = [r["generated_path"] for r in rows]
    duplicates = sorted({t for t in targets if targets.count(t) > 1})
    if duplicates:
        sys.exit(f"publish: name collision(s) in the manifest: {', '.join(duplicates)}")
    return rows


def copy_sources(rows: list[dict]) -> int:
    """Copy every source into paper/generated; return the number of new or changed files."""
    missing = [r for r in rows if not (TASK_OUTPUT_ROOT / r["source"]).is_file()]
    if missing:
        lines = [f"  {r['source']}  <- {r['producing_script']}" for r in missing]
        sys.exit("publish: missing source file(s); run `python -m SCons` first:\n" + "\n".join(lines))

    changed = 0
    for r in rows:
        source, destination = TASK_OUTPUT_ROOT / r["source"], GENERATED / r["generated_path"]
        before = sha256(destination) if destination.is_file() else None
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        status = "new" if before is None else ("changed" if before != sha256(destination) else "unchanged")
        changed += status != "unchanged"
        print(f"  {status:9s} {r['generated_path']}")
    return changed


def unresolved_references() -> list[str]:
    """Return the references in the documents that do not point to an existing file.

    Paths are read as LaTeX reads them when the document is compiled from its own folder: `\\input` relative
    to that folder, `\\includegraphics` relative to it and to each folder in `\\graphicspath`.
    """
    unresolved = []
    for doc in documents():
        commands = tex_commands(doc)
        graphics_dirs = [doc.parent]
        for command, argument in commands:
            if command == "graphicspath":  # \graphicspath{{dir1/}{dir2/}}
                graphics_dirs += [doc.parent / d for d in re.findall(r"\{([^{}]*)\}", argument)]
        for command, target in commands:
            if command == "includegraphics":
                bases, extensions = graphics_dirs, GRAPHICS_EXTENSIONS
            elif command == "input":
                bases, extensions = [doc.parent], ["", ".tex"]
            else:
                continue
            if not any((base / (target + ext)).is_file() for base in bases for ext in extensions):
                unresolved.append(f"{doc.relative_to(PAPER).as_posix()}: \\{command}{{{target}}}")
    return unresolved


def mirror_to_shared(destination: Path) -> None:
    """Copy paper/generated/ into `destination`, replacing files that changed."""
    for path in GENERATED.rglob("*"):
        if path.is_file():
            target = destination / path.relative_to(GENERATED)
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.is_file() or sha256(target) != sha256(path):
                shutil.copy2(path, target)
    print(f"publish: mirrored paper/generated to {destination}")


def main() -> None:
    """Publish the paper inputs."""
    rows = read_manifest()
    changed = copy_sources(rows)
    print(f"publish: {len(rows)} files copied, {changed} new/changed")

    listed = {r["generated_path"] for r in rows}
    extra = [p.relative_to(GENERATED).as_posix() for p in GENERATED.rglob("*")
             if p.is_file() and p.relative_to(GENERATED).as_posix() not in listed]
    if extra:
        print(f"publish: warning: files in paper/generated not in the manifest: {extra}")

    unresolved = unresolved_references()
    if unresolved:
        sys.exit("publish: unresolved reference(s):\n" + "\n".join(f"  {u}" for u in unresolved))
    print("publish: all includegraphics / input references resolve")

    if SHARED_OUTPUT_ROOT is not None:
        mirror_to_shared(SHARED_OUTPUT_ROOT / "generated")


if __name__ == "__main__":
    main()
