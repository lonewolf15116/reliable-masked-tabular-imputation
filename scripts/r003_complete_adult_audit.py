#!/usr/bin/env python3
"""R003 supplementary Adult audit. Audit-only: no splitting, fitting or model evaluation.
Run: python scripts/r003_complete_adult_audit.py
Reads the locally acquired adult.data, cross-checks source audit, appends audited fields.
"""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

SOURCE = Path("artifacts/source/adult.data")
AUDIT = Path("artifacts/source/adult_source_audit.json")
COLUMNS = ["age","workclass","fnlwgt","education","education-num",
           "marital-status","occupation","relationship","race","sex",
           "capital-gain","capital-loss","hours-per-week","native-country","income"]
NUMERIC = {"age","fnlwgt","education-num","capital-gain","capital-loss","hours-per-week"}
HASH = "5b00264637dbfec36bdeaab5676b0b309ff9eb788d63554ca0a249491c86603d"

def audit():
    raw = SOURCE.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != HASH:
        raise SystemExit("STOP: Adult bytes differ from verified candidate reference")
    existing = json.loads(AUDIT.read_text(encoding="utf-8"))
    if existing.get("sha256_of_original_unmodified_bytes") != digest:
        raise SystemExit("STOP: source audit SHA differs from actual source")
    decoded = raw.decode("utf-8")
    raw_rows = [r for r in csv.reader(decoded.splitlines()) if r]
    if len(raw_rows) != 32561 or any(len(row) != 15 for row in raw_rows):
        raise SystemExit("STOP: structure differs from expected Adult training source")
    rows = [[v.strip() for v in row] for row in raw_rows]
    before = {name:len({r[i] for r in raw_rows}) for i,name in enumerate(COLUMNS) if name not in NUMERIC}
    after = {name:len({r[i] for r in rows}) for i,name in enumerate(COLUMNS) if name not in NUMERIC}
    qcounts = {name:sum(r[i]=="?" for r in rows) for i,name in enumerate(COLUMNS)}
    if qcounts != existing["question_mark_count_per_column"]:
        raise SystemExit("STOP: question-mark counts changed after parsing")
    if any(r[i] in ("", "nan", "NaN", "None") for r in rows for i in range(15)):
        raise SystemExit("STOP: empty / NaN-like category seen in original dataset")
    labels = Counter(r[-1] for r in rows)
    if set(labels) != {"<=50K",">50K"}:
        raise SystemExit(f"STOP: unexpected income labels: {labels}")
    qcols = [i for i,n in enumerate(COLUMNS) if qcounts[n] != 0]
    all_question = sum(all(r[i]=="?" for i in qcols) for r in rows)
    near_question = sum(sum(r[i]=="?" for i in qcols) >= max(1,len(qcols)-1) for r in rows)
    for i,name in enumerate(COLUMNS):
        if name in NUMERIC and any(not r[i].lstrip("-").isdigit() for r in rows):
            raise SystemExit(f"STOP: invalid numeric field {name}")
    add={
        "source_revision":"R003-audit-only-v1",
        "adult_test_used":False,
        "all_splits_source":"adult.data only (32561 rows)",
        "whitespace_policy":"strip every parsed field for ALL downstream consumers; retain source bytes unchanged for SHA256",
        "categorical_cardinality_pre_strip":before,
        "categorical_cardinality_post_strip":after,
        "income_balance":dict(sorted(labels.items())),
        "income_balance_fraction":{k:v/len(rows) for k,v in sorted(labels.items())},
        "question_mark_fraction_per_column":{k:v/len(rows) for k,v in qcounts.items()},
        "question_mark_category_policy":"observed categorical value, not null/NaN; downstream encoder must preserve explicit '?' level",
        "rows_all_question_mark_among_original_question_mark_columns":all_question,
        "rows_at_least_two_question_marks_among_original_question_mark_columns":near_question,
        "row_policy":"retain every row; ineligible cells are flagged per feature rather than dropping rows",
        "split_state":"NOT ASSIGNED; requires approved split seed, stratified fractions and immutable index manifest",
        "numerical_training_iqr_state":"NOT CALCULATED; requires approved training split",
        "excluded_zero_iqr_features_state":"PENDING TRAINING SPLIT; keep flagged separately, not silently omitted",
        "eligible_cell_manifest_state":"PENDING approved split and feature/anchor review",
        "no_training_or_model_fitting_performed":True
    }
    # Original acquisition record stays intact: only append supplementary audited fields.
    for k in add:
        if k in existing and existing[k] != add[k]:
            raise SystemExit(f"STOP: existing audit field conflict {k}")
    existing.update(add)
    AUDIT.write_text(json.dumps(existing,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:existing[k] for k in ("income_balance","categorical_cardinality_pre_strip",
      "categorical_cardinality_post_strip","rows_all_question_mark_among_original_question_mark_columns",
      "rows_at_least_two_question_marks_among_original_question_mark_columns","split_state")},indent=2))
    print("Source SHA256 verified; supplementary Adult audit written. G1B STILL BLOCKED.")

if __name__=="__main__":
    audit()
