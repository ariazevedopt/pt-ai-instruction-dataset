# LusoSupport-PT — dataset pipeline shortcuts
.PHONY: install generate validate dedupe export stats pipeline test clean

install:
	pip install -r requirements.txt

# Generate 100 synthetic rows → datasets/interim/generated.jsonl
generate:
	cd scripts && python3 generate.py --n 100

# Validate the processed dataset
validate:
	cd scripts && python3 -c "\
import json, sys; sys.path.insert(0,'scripts'); \
from validate import is_valid_row; \
rows=[json.loads(l) for l in open('datasets/processed/lusosupport_pt_v1.jsonl') if l.strip()]; \
bad=[r['id'] for r in rows if not is_valid_row(r)]; \
print(f'{len(rows)-len(bad)}/{len(rows)} rows valid'); \
[print('  FAIL:', i) for i in bad]"

# Deduplicate the processed dataset (in-place)
dedupe:
	cd scripts && python3 dedupe.py \
		../datasets/processed/lusosupport_pt_v1.jsonl \
		../datasets/processed/lusosupport_pt_v1.jsonl

# Export to CSV, Alpaca JSONL, and Parquet
export:
	cd scripts && python3 export_formats.py \
		../datasets/processed/lusosupport_pt_v1.jsonl \
		--csv ../datasets/processed/lusosupport_pt_v1.csv \
		--alpaca ../datasets/processed/lusosupport_pt_v1_alpaca.jsonl \
		--parquet ../datasets/processed/lusosupport_pt_v1.parquet

# Print dataset statistics
stats:
	cd scripts && python3 export_formats.py \
		../datasets/processed/lusosupport_pt_v1.jsonl \
		--stats

# Full pipeline: generate → validate → deduplicate → save
pipeline:
	cd scripts && python3 pipeline.py --n 100 --stats

clean:
	rm -f datasets/interim/generated.jsonl
	rm -f datasets/processed/lusosupport_pt_v1.csv
	rm -f datasets/processed/lusosupport_pt_v1_alpaca.jsonl
	rm -f datasets/processed/lusosupport_pt_v1.parquet

test:
	python3 -m pytest tests/ -v
