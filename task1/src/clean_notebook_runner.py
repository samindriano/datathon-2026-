"""Execute plain-Python notebook code cells in a fresh interpreter process."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def execute_notebook(path: Path) -> None:
    notebook = json.loads(Path(path).read_text(encoding="utf-8"))
    if notebook.get("nbformat") != 4 or not isinstance(notebook.get("cells"), list):
        raise ValueError("Expected a valid nbformat 4 notebook")
    namespace = {"__name__": "__main__"}
    for index, cell in enumerate(notebook["cells"]):
        if cell.get("cell_type") != "code":
            continue
        source = cell.get("source", [])
        code = "".join(source) if isinstance(source, list) else str(source)
        if not code.strip():
            continue
        exec(compile(code, f"{path}#cell-{index}", "exec"), namespace)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notebook", type=Path)
    args = parser.parse_args()
    execute_notebook(args.notebook)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
