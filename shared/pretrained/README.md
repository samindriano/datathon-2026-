# Pretrained Model Pantry

Folder ini menyiapkan kandidat open-weight sebelum task dibuka. Kandidat di
sini bukan baseline resmi dan tidak boleh dipilih sebelum problem statement,
data, target, metric, serta validation scheme diperiksa.

## Kandidat yang disiapkan

| Candidate | Modality | Model | License | Peran awal |
|---|---|---|---|---|
| `text-minilm-l6` | Text | `sentence-transformers/all-MiniLM-L6-v2` | Apache-2.0 | Embedding/encoder ringan |
| `vision-vit-base-224` | Image | `google/vit-base-patch16-224` | Apache-2.0 | Backbone klasifikasi gambar |
| `timeseries-chronos-t5-tiny` | Time series | `amazon/chronos-t5-tiny` | Apache-2.0 | Kandidat forecasting kecil |

Untuk data tabular, mulai dari baseline CatBoost/LightGBM/XGBoost. Jangan
memaksakan pretrained model.

Metadata lengkap dan revision policy berada di `candidates.json`. Model card:

- https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- https://huggingface.co/google/vit-base-patch16-224
- https://huggingface.co/amazon/chronos-t5-tiny

## Malam sebelum task

1. Review model card dan lisensi.
2. Pilih hanya bundle yang benar-benar ingin dicache.
3. Install downloader pada environment terpisah:

   ```bash
   python -m pip install -r shared/pretrained/requirements-download.txt
   ```

4. Lihat rencana tanpa download:

   ```bash
   python shared/pretrained/prepare_candidate.py text-minilm-l6 --dry-run
   ```

5. Download satu candidate secara eksplisit:

   ```bash
   python shared/pretrained/prepare_candidate.py text-minilm-l6 --download
   ```

6. Verifikasi file dan hasilkan receipt checksum:

   ```bash
   python shared/pretrained/verify_bundle.py shared/pretrained/bundles/text-minilm-l6
   ```

7. Upload folder bundle yang lolos verifikasi sebagai private Kaggle Dataset
   milik tim. Catat Kaggle path dan receipt di `coordination/TEAM_STATUS.md`.

`cache/` dan `bundles/` di-ignore oleh Git agar weights besar tidak ter-commit.
Receipt boleh disalin ke experiment directory jika kandidat benar-benar dipakai.

## Gate pemilihan besok

Gunakan candidate hanya jika semua jawaban berikut `YES`:

- Modality dan output head cocok dengan task.
- Lisensi dan open-weight status masih terverifikasi.
- Seluruh file tersedia offline di Kaggle.
- Loader berjalan dengan `local_files_only=True` atau ekuivalennya.
- Fine-tuning hanya memakai competition training data.
- Validation menggunakan scheme resmi dan kandidat mengalahkan baseline secara
  stabil, bukan hanya public leaderboard.
- Runtime dan memory aman untuk batas lomba.

Jika salah satu belum jelas, status candidate adalah `INVESTIGATE`, bukan
`KEEP` atau `FINAL_CANDIDATE`.

## Larangan

- Jangan memakai hosted inference/API untuk modeling atau prediction.
- Jangan fine-tune dengan external data.
- Jangan mengunduh model dari notebook final.
- Jangan menaruh token Hugging Face/Kaggle dalam repository atau notebook.
- Jangan menganggap contoh input pada model card sebagai data kompetisi.
