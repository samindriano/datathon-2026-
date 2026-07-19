"""Execute notebook code cells sequentially without Jupyter dependencies."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notebook", type=Path)
    args = parser.parse_args()
    notebook_path = args.notebook.resolve()
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    namespace = {"__name__": "__main__"}
    for index, cell in enumerate(notebook.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        exec(compile(source, f"{notebook_path}#cell-{index}", "exec"), namespace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
