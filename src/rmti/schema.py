"""G1A schema validation only. No prediction model."""
FIELDS = ('dataset','split','split_seed','mask_seed','model_seed','mechanism','level','feature','row_id','cell_id','true_value','predicted_value','uncertainty_score','interval_lower','interval_upper','accepted_flag','review_rank')
def validate(records):
    for record in records:
        if set(record) != set(FIELDS): raise ValueError('schema mismatch')
        if record['split'] not in ('train','validation','test'): raise ValueError('split')
        if record['mechanism'] not in ('MCAR','MAR','MNAR_STRESS'): raise ValueError('mechanism')
        if not isinstance(record['accepted_flag'],bool): raise ValueError('accepted_flag')
    return True
