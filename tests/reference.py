"""Reference hashes: record what a verified output looked like, so a test notices when it changes.

`reference_outputs.json` maps "<task>/<file>" (under OUTPUT_ROOT/tasks/) to the SHA-256 hash of that output.
Text files (.csv, .tex, .txt, .json, .md) are hashed with LF line endings, so Windows and macOS agree; other files
are hashed byte for byte. Figures are best left out: their bytes differ across systems and library versions.

Record or update entries after checking the outputs by hand (run the build first):

    python tests/reference.py 02_example_analysis/table_production.tex 01_example_clean/panel.csv
"""

import hashlib
import json
import sys
from pathlib import Path

REFERENCE_FILE = Path(__file__).with_name("reference_outputs.json")
TEXT_SUFFIXES = {".csv", ".tex", ".txt", ".json", ".md"}


def digest(path: Path) -> str:
    """SHA-256 of a file; text files with line endings normalized to LF."""
    data = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def load() -> dict[str, str]:
    """Return the recorded hashes, {"<task>/<file>": sha256}."""
    if not REFERENCE_FILE.is_file():
        return {}
    return json.loads(REFERENCE_FILE.read_text(encoding="utf-8"))


def record(relative_paths: list[str]) -> None:
    """Hash the given outputs and store them in reference_outputs.json."""
    from project_package.config import TASK_OUTPUT_ROOT

    reference = load()
    for relative in relative_paths:
        path = TASK_OUTPUT_ROOT / relative
        if not path.is_file():
            sys.exit(f"{path} not found; run the build first")
        reference[relative] = digest(path)
        print(f"recorded {relative}")
    REFERENCE_FILE.write_text(json.dumps(reference, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    record(sys.argv[1:])
