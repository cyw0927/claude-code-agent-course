"""전처리 · 중복 제거. Notebook STEP 05~06에서 검증된 로직을 그대로 옮긴다."""

import pandas as pd

from src.collector import DATA_SPEC_COLUMNS


def build_dataframe(jobs: list[dict]) -> pd.DataFrame:
    """딕셔너리 리스트를 DATA_SPEC 컬럼 순서의 DataFrame으로 변환한다."""
    return pd.DataFrame(jobs, columns=DATA_SPEC_COLUMNS)


def clean_jobs(df: pd.DataFrame) -> pd.DataFrame:
    """빈 문자열을 결측치(pd.NA)로 통일하고, job_url 기준 중복을 제거한다."""
    df_clean = df.replace("", pd.NA)
    df_dedup = df_clean.drop_duplicates(subset=["job_url"], keep="first")
    return df_dedup
