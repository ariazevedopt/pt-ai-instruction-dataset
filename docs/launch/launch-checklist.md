# LusoSupport-PT — Launch Checklist

Step-by-step guide to publish and launch the dataset.

---

## Pre-launch (complete before posting anywhere)

- [ ] **Merge PR #48** — HF Lite slice, dataset card, licences ✅
- [ ] **Merge PR #49** — FUNDING.yml ✅
- [ ] **Create HF dataset repo** (issue #11)
  1. Go to https://huggingface.co/new-dataset
  2. Name: `LusoSupport-PT`, visibility: Public
  3. Upload `datasets/hf-lite/lusosupport_pt_lite.jsonl`
  4. Upload `datasets/hf-lite/README.md` as the dataset card
  5. Confirm dataset is accessible and renders correctly
- [ ] **Set up Gumroad products** (issue #26)
  1. Go to https://app.gumroad.com → New Product
  2. Individual (€39): upload `lusosupport_pt_v1.jsonl` + CSV + Alpaca JSONL + Parquet + `LICENCE-COMMERCIAL.md`
  3. Commercial (€149): same files + `LICENCE-COMMERCIAL.md` commercial tier
  4. Update Gumroad URLs in `datasets/hf-lite/README.md` and `README.md`
- [ ] **Activate GitHub Sponsors** (issue #27)
  1. Go to https://github.com/sponsors
  2. Follow setup wizard
  3. `FUNDING.yml` is already in place — the button will appear once sponsors is active

---

## Launch day

- [ ] Post on r/MachineLearning (see `docs/launch/announcement-templates.md`)
- [ ] Post on r/LocalLLaMA
- [ ] Post on r/datasets
- [ ] Post in HF Community Forum
- [ ] Post on LinkedIn

---

## Post-launch

- [ ] Record Month 1 metrics in `docs/launch/metrics-tracking.md`
- [ ] Respond to any comments / questions within 48 h
- [ ] Open issues for any bugs or requests received

---

## Files reference

| File | Purpose |
|---|---|
| `datasets/hf-lite/lusosupport_pt_lite.jsonl` | 200-row free slice for HF |
| `datasets/hf-lite/README.md` | HF dataset card |
| `datasets/processed/lusosupport_pt_v1.jsonl` | Full 5,163-row dataset (Gumroad) |
| `datasets/processed/lusosupport_pt_v1.csv` | CSV export |
| `datasets/processed/lusosupport_pt_v1_alpaca.jsonl` | Alpaca JSONL export |
| `datasets/processed/lusosupport_pt_v1.parquet` | Parquet export |
| `LICENCE` | CC BY 4.0 (free tier) |
| `LICENCE-COMMERCIAL.md` | Commercial licence (Gumroad) |
| `docs/launch/announcement-templates.md` | Reddit / HF / LinkedIn post copy |
| `docs/launch/metrics-tracking.md` | Monthly metrics log |
