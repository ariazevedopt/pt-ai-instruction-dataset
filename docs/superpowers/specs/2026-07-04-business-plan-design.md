# LusoSupport-PT — Business Plan & Monetization Design

**Date:** 2026-07-04  
**Author:** @ariazevedopt  
**Status:** Approved — implementation in progress

---

## Problem

Most publicly available Portuguese NLP datasets are either broad generic corpora, academic benchmarks, or heavily pt-BR oriented. There is no structured, PT-PT customer support instruction dataset optimised for LLM fine-tuning. This is a real gap that LusoSupport-PT fills.

---

## Goal

Generate sustainable **passive income** from a niche PT-PT instruction dataset by publishing a free discovery version and selling a premium product — without ongoing active work once the initial build is complete.

---

## Revenue Model: Freemium + Commercial Licence

### Tier 1 — Free (Hugging Face)
- **~200 high-quality rows** (one per domain × task type combination, hand-curated)
- Available at `huggingface.co/datasets/ariazevedopt/LusoSupport-PT`
- Licence: CC BY 4.0 (free for any use with attribution)
- **Purpose:** discovery, credibility, SEO, community trust

### Tier 2 — Premium Individual (Gumroad, €39)
- **1,000+ rows** across all 8 domains, 8 task types, 17 intents
- Formats: JSONL, CSV, Alpaca JSONL (fine-tuning ready)
- Dataset card + schema documentation PDF
- Includes all future v1.x updates
- Licence: personal/research/non-commercial use

### Tier 3 — Commercial Licence (Gumroad, €149)
- Everything in Tier 2
- Explicit commercial use rights (use in products, APIs, internal tooling)
- Simple single-page licence agreement (based on standard commercial data licence)

### Tier 4 — GitHub Sponsors (pay-what-you-want)
- Set up FUNDING.yml for community contributors who want to support ongoing work
- Low effort, set-and-forget

### Future revenue (v2+)
- `LusoSupport-PT-BR` — Brazilian Portuguese variant (separate product)
- Industry vertical packs — healthcare, legal, fintech PT-PT subsets
- Custom dataset orders — bespoke domains/task types on request (active work)

---

## Milestone Roadmap

### ✅ M1 — Dataset Planning
Foundation: niche chosen, schema defined, sample data created, repo structured.

### ⏳ M2 — Data Generation (target: July 18, 2026)
Working generation pipeline. Currently at 60 rows; target: pipeline producing 1,000+ rows.
- Key blocker: `generate_output()` still returns placeholder stubs — needs realistic PT-PT responses.

### ⏳ M3 — Cleaning & Validation (target: July 25, 2026)
Deduplication, validation, and manual quality review of 50+ random samples.

### ⏳ M4 — HF Lite Launch (target: August 1, 2026)
Publish free ~200-row version on Hugging Face. Dataset card, licence, usage examples.
This is the **traffic and credibility** milestone — no money yet, but the funnel opens.

### 🆕 M5 — Quality & Scale (target: August 22, 2026)
Reach 1,000+ quality rows suitable for the paid product. Improve output realism. Manual spot-check.

### 🆕 M6 — Monetization Setup (target: September 5, 2026)
Gumroad product pages (Individual + Commercial), licence texts, GitHub Sponsors FUNDING.yml, README badges and buy links.

### 🆕 M7 — Full Launch & Promotion (target: September 19, 2026)
Announce across LinkedIn, Reddit (r/MachineLearning, r/LocalLLaMA), X, HF community forum. First paying customer target.

### 🆕 M8 — Growth & Iteration (target: December 31, 2026)
Monthly check-ins: HF download tracking, Gumroad sales review, feedback-driven improvements, v2 scoping.

---

## Success Criteria

| Metric | Target | By |
|--------|--------|----|
| HF downloads | ≥ 100 | 30 days after M4 |
| GitHub stars | ≥ 20 | 30 days after M7 |
| First Gumroad sale | 1 | 30 days after M6 |
| Monthly revenue | ≥ €50 | Month 3 post-launch |
| Monthly revenue | ≥ €150 | Month 6 post-launch |

---

## Distribution & Marketing Strategy

**HF as top-of-funnel:**  
Hugging Face has a built-in audience of ML practitioners searching for datasets. Good dataset metadata, tags, and a detailed card will surface the dataset organically. The free version converts to paid when users hit scale or commercial needs.

**GitHub as credibility signal:**  
Stars, a clean README, and the pipeline code show this is a maintained, serious project — not a one-off dump.

**Content marketing (low-effort):**  
One LinkedIn post per milestone. One Reddit thread at launch. These compound over time via search.

**SEO via HF + GitHub:**  
Targeting keywords: "Portuguese NLP dataset", "PT-PT instruction dataset", "fine-tuning Portuguese LLM", "European Portuguese support dataset". Both HF and GitHub rank well in Google.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Output quality too low to sell | Manual review milestone (M3); quality bar in validation |
| Small PT-PT market | Price accordingly (€39 is accessible); expand to pt-BR in v2 |
| Free HF version cannibalises sales | Free tier capped at ~200 rows; paid version is 5× larger with extras |
| No marketing budget | Organic-only strategy; rely on HF discovery + one-time social posts |

---

## Technical Prerequisites (before monetization)

- [ ] `generate_output()` produces realistic PT-PT responses per task type (not stubs)
- [ ] ≥ 1,000 rows passing `is_valid_row()` in processed dataset
- [ ] Zero rows containing placeholder outputs (`"Resposta gerada."`)
- [ ] All 8 domains × 8 task types covered with ≥ 10 rows each
- [ ] Manual quality review completed and documented
