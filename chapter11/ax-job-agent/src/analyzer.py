"""신규 공고 판별 · 기본 분석 · AX 관련 필터링. Notebook STEP 07~08 로직을 그대로 옮긴다."""

from pathlib import Path

import pandas as pd

from src.collector import DATA_SPEC_COLUMNS


def find_new_jobs(df_dedup: pd.DataFrame, history_path: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """history_path(job_url 목록이 있는 CSV)와 비교해 신규/기존 공고를 나눈다.

    반환값: (new_jobs_df, existing_jobs_df, history_df)
    """
    if history_path.exists():
        history_df = pd.read_csv(history_path)
        known_urls = set(history_df["job_url"])
    else:
        history_df = pd.DataFrame(columns=DATA_SPEC_COLUMNS)
        known_urls = set()

    is_new = ~df_dedup["job_url"].isin(known_urls)
    new_jobs_df = df_dedup[is_new].copy()
    existing_jobs_df = df_dedup[~is_new].copy()
    return new_jobs_df, existing_jobs_df, history_df


def save_job_history(df_dedup: pd.DataFrame, history_df: pd.DataFrame, history_path: Path) -> None:
    """성공적으로 처리한 공고를 다음 실행의 신규 판별 기록으로 저장한다."""
    combined = pd.concat([history_df, df_dedup], ignore_index=True)
    combined = combined.drop_duplicates(subset=["job_url"], keep="last")
    history_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(history_path, index=False, encoding="utf-8-sig")


def analyze_jobs(df_dedup: pd.DataFrame, new_jobs_df: pd.DataFrame, existing_jobs_df: pd.DataFrame) -> dict:
    """pandas로 계산 가능한 통계를 dict로 반환한다."""
    return {
        "total": len(df_dedup),
        "new": len(new_jobs_df),
        "existing": len(existing_jobs_df),
        "by_company": df_dedup["company_name"].value_counts().to_dict(),
        "by_location": df_dedup["location"].value_counts(dropna=False).to_dict(),
        "by_career": df_dedup["career"].value_counts(dropna=False).to_dict(),
        "by_search_keyword": df_dedup["search_keyword"].value_counts().to_dict(),
    }


def filter_ax_related(df_dedup: pd.DataFrame) -> pd.DataFrame:
    """job_title에 'AX' 또는 'AI'가 포함된 공고만 남긴다 (단순 키워드 규칙)."""
    is_ax_related = (
        df_dedup["job_title"].str.contains("AX", case=True, na=False)
        | df_dedup["job_title"].str.contains("AI", case=True, na=False)
    )
    return df_dedup[is_ax_related]
