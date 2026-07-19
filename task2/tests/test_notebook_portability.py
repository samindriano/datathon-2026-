import json
import unittest
from pathlib import Path


NOTEBOOK = (
    Path(__file__).resolve().parents[1]
    / "notebooks"
    / "EnterYourTeamName_Task2_Notebook.ipynb"
)


class NotebookPortabilityTest(unittest.TestCase):
    def test_numeric_hash_remains_fail_closed_but_csv_bytes_are_portable(self):
        notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
        source = "\n".join(
            "".join(cell.get("source", []))
            for cell in notebook["cells"]
            if cell.get("cell_type") == "code"
        )
        self.assertIn("Prediction hash mismatch", source)
        self.assertNotIn("raise RuntimeError(f'CSV hash mismatch", source)
        self.assertIn("csv_matches_local_reference", source)


if __name__ == "__main__":
    unittest.main()
