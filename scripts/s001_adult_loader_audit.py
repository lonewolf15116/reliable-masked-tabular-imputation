#!/usr/bin/env python3
"""S001 loading contract audit. No model fitting, splitting or encoding."""
import csv
import hashlib
import io
import json
from pathlib import Path

import pandas as pd

PATH=Path("artifacts/source/adult.data")
AUDIT=Path("artifacts/source/adult_source_audit.json")
SHA="5b00264637dbfec36bdeaab5676b0b309ff9eb788d63554ca0a249491c86603d"
COLS=["age","workclass","fnlwgt","education","education-num","marital-status",
      "occupation","relationship","race","sex","capital-gain","capital-loss",
      "hours-per-week","native-country","income"]
CAT=["workclass","education","marital-status","occupation","relationship","race",
     "sex","native-country","income"]
EXPECTED_Q={"workclass":1836,"occupation":1843,"native-country":583}
EXPECTED_CARD={"workclass":9,"education":16,"marital-status":7,"occupation":15,
               "relationship":6,"race":5,"sex":2,"native-country":42,"income":2}

def main():
    raw=PATH.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:
        raise RuntimeError("raw Adult source hash mismatch")
    rows=list(csv.reader(io.StringIO(raw.decode("utf-8"))))
    if len(rows)!=32561 or any(len(r)!=15 for r in rows):
        raise RuntimeError("source row/column mismatch")
    # We count actual padding, not an inference based on cardinality.
    raw_padding={name:sum(r[i]!=r[i].strip() for r in rows)
                 for i,name in enumerate(COLS)}
    original_card={name:len(set(r[i] for r in rows))
                   for i,name in enumerate(COLS) if name in CAT}
    df=pd.read_csv(PATH,header=None,names=COLS,skipinitialspace=True,
                   keep_default_na=False,na_filter=False)
    for name in CAT:
        df[name]=df[name].astype(str).str.strip()
    if len(df)!=32561 or df.isna().any().any():
        raise AssertionError("rows lost or NA introduced")
    q={name:int((df[name]=="?").sum()) for name in EXPECTED_Q}
    if q!=EXPECTED_Q:
        raise AssertionError(f"lost literal question-mark category: {q}")
    after={name:int(df[name].nunique(dropna=False)) for name in CAT}
    if after!=EXPECTED_CARD:
        raise AssertionError(f"categorical counts mismatch: {after}")
    if set(df.income)!={"<=50K",">50K"}:
        raise AssertionError("income labels incorrect after strip")
    record=json.loads(AUDIT.read_text(encoding="utf-8"))
    if record.get("sha256_of_original_unmodified_bytes")!=SHA:
        raise AssertionError("source audit identity mismatch")
    record["parser_contract"]={
        "pandas_call":"pd.read_csv(path,header=None,names=COLS,skipinitialspace=True,keep_default_na=False,na_filter=False) followed by .astype(str).str.strip() on categorical columns",
        "pre_strip_categorical_cardinality":original_card,
        "post_strip_categorical_cardinality_including_question_mark":after,
        "per_column_raw_padding_rows":raw_padding,
        "literal_question_mark_counts_survive_loading":q,
        "question_marks_coerced_to_null":False,
        "row_count":int(len(df)),"all_fields_have_nonnull_values":True,
        "adult_test_used":False
    }
    AUDIT.write_text(json.dumps(record,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(record["parser_contract"],indent=2))
    print("PASS loading contract — actual raw padding measured; literal ? values preserved; audit JSON updated.")

if __name__=="__main__":
    main()
