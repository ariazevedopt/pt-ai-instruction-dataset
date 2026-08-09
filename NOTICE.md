# NOTICE

## Licence scope

This repository is licensed under the **Apache License 2.0** (see [`LICENSE`](LICENSE)).
That licence covers the **tooling** in this repository: the generation
pipeline orchestration, schema/config definitions, validation logic,
deduplication, export formats, and quality reporting.

It does **not** cover, and does **not** include, the following:

- `scripts/scenarios.py`
- `scripts/templates.py`
- `scripts/responses.py`
- `scripts/responses_expansion.py`
- `scripts/responses_expansion_v2.py`

These modules contain the actual hand-tuned pt-PT customer-message and
agent-response content — the vocabulary, phrasing variety, and tone
handling that make the generated dataset linguistically realistic and
commercially valuable. They are proprietary, are **not distributed** with
this public repository, and are required to run `make generate` /
`make pipeline` end-to-end. A handful of tests that exercise these
modules (`tests/test_scenarios_tones.py`, `tests/test_templates.py`,
`tests/test_responses_expansion_v2.py`) are likewise excluded.

## Why

LusoSupport-PT's dataset generation pipeline (structure, validation
rules, taxonomy, export tooling) is open source so the methodology is
transparent, auditable, and reusable by the community. The **content**
that pipeline operates on — the actual seed messages and response
templates — is what is sold as the finished dataset on
[Gumroad](https://ariazevedo.gumroad.com/l/lusosupport-pt) (individual
and commercial licences). Cloning this repository and running the public
pipeline alone will not reproduce the released dataset.

## Using the dataset itself

The released dataset files (`datasets/processed/*.jsonl`, `.csv`,
`.parquet`) are governed by their own product licence terms (individual
or commercial), not by the Apache-2.0 licence on this repository's code.
See the free 200-row sample on
[Hugging Face](https://huggingface.co/datasets/ariazevedo/LusoSupport-PT)
(CC BY 4.0) or the full dataset's licence terms on Gumroad for details.

## Questions / licensing

For commercial licensing questions, or if you believe this repository's
public tooling doesn't reflect this notice accurately, please open an
issue on GitHub.
