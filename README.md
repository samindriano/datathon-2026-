# Datathon 2026

Repository kerja tim untuk Kaggle Task 1 (18 Juli 2026) dan Task 2
(19 Juli 2026).

## Mulai di sini

1. Baca [`AGENTS.md`](AGENTS.md).
2. Baca status terbaru di [`coordination/TEAM_STATUS.md`](coordination/TEAM_STATUS.md).
3. Pastikan task dan owner Anda tercatat sebelum mulai bekerja.
4. Jangan commit raw competition data, credential, weights besar, atau output
   sementara.

Clone repository:

```bash
git clone https://github.com/samindriano/datathon-2026-.git
cd datathon-2026-
```

Sebelum membuat perubahan:

```bash
git status
git pull
```

## Struktur

```text
datathon-2026/
├── AGENTS.md
├── README.md
├── requirements.txt
├── coordination/
│   └── TEAM_STATUS.md
├── shared/
│   └── pretrained/
├── task1/
│   ├── src/
│   ├── configs/
│   ├── experiments/
│   ├── notebooks/
│   ├── reports/
│   └── submissions/
└── task2/
    ├── src/
    ├── configs/
    ├── experiments/
    ├── notebooks/
    ├── reports/
    └── submissions/
```

`task1/` dan `task2/` harus diperlakukan sebagai task terpisah. Jangan membawa
asumsi target, metric, validation, feature, atau model dari satu task ke task
lain tanpa verifikasi.

## Workflow branch

Branch `main` harus stabil. Setelah baseline resmi tersedia, eksperimen dibuat
di branch terpisah, misalnya:

```text
exp/d1-main-model
exp/d1-person2-alternative
exp/d1-person3-feature
```

Satu eksperimen menguji satu hipotesis dan dicatat di folder
`taskN/experiments/EXP-.../` serta `TEAM_STATUS.md`.

## Pretrained pantry

Tooling persiapan open-weight berada di
[`shared/pretrained/`](shared/pretrained/README.md). Kandidat di sana belum
menjadi baseline dan tidak diunduh otomatis. Setelah task dibuka, pilih hanya
candidate yang cocok dan lolos validation resmi.

## Dependency

`requirements.txt` sengaja minimal selama fase preparation. Tambahkan dependency
setelah modality dan kebutuhan task terbukti, lalu pin versi yang dipakai final.
