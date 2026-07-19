# Task 2

Kaggle Task 2 — 19 Juli 2026. Mulai analisis dari nol; jangan mengasumsikan
dataset, target, metric, validation, feature, model, atau submission schema sama
dengan Task 1.

- `src/`: reusable training, feature, validation, dan inference code.
- `configs/`: konfigurasi eksperimen.
- `experiments/`: satu folder per experiment ID.
- `notebooks/`: exploration dan final inference notebook.
- `reports/`: evidence, analysis, dan writeup material.
- `submissions/`: output versioned; jangan overwrite file lama.
- `data/`: local/Kaggle competition data; di-ignore dan tidak boleh diubah.

## Baseline lokal

Jalankan dari root repository:

```powershell
$env:PYTHONPATH = "$PWD\task2\src"
python task2\src\run_baseline.py `
  --data-root task2\data\competition\dataset-task2 `
  --experiment-dir task2\experiments\d2-e001-baseline
```

Notebook inference dapat dijalankan langsung di VS Code/Jupyter:

```text
task2/notebooks/EnterYourTeamName_Task2_Notebook.ipynb
```

Notebook mencari data lokal secara relatif atau di `/kaggle/input`, dengan
override opsional `TASK2_DATA_DIR`. Output lokal ditulis ke
`task2/submissions/submission.csv`; output Kaggle ditulis ke
`/kaggle/working/submission.csv`. `TASK2_SUBMISSION_PATH` dapat dipakai untuk
override eksplisit.
