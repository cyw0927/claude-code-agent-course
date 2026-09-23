"""잡코리아, 고용24 또는 로컬 샘플에서 채용공고를 수집한다."""

import os
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

from src.jobkorea_client import collect_jobkorea_jobs
from src.work24_client import DATA_SPEC_COLUMNS, Work24ConfigError, collect_work24_jobs


def load_sample_jobs(project_root: Path, search_keyword: str = "AX") -> list[dict]:
    """네트워크 없이 파이프라인을 검증하기 위한 가상 공고를 읽는다."""
    sample_path = project_root / "data" / "raw" / "sample_jobs.html"
    with open(sample_path, encoding="utf-8") as file:
        soup = BeautifulSoup(file.read(), "html.parser")

    jobs = []
    for index, item in enumerate(soup.select(".job-item"), start=1):
        title_tag = item.select_one(".title a")
        jobs.append({
            "company_name": item.select_one(".company").get_text(strip=True),
            "job_title": title_tag.get_text(strip=True),
            "career": item.select_one(".career").get_text(strip=True),
            "location": item.select_one(".location").get_text(strip=True),
            "posted_date": item.select_one(".date-posted").get_text(strip=True),
            "closing_date": item.select_one(".date-closing").get_text(strip=True),
            "job_url": f"sample://job/{index}",
            "search_keyword": search_keyword,
            "collected_at": datetime.now().isoformat(timespec="seconds"),
        })
    return jobs


def collect_jobs(
    project_root: Path,
    search_keyword: str = "AX",
    require_live: bool = False,
    force_sample: bool = False,
    source: str = "jobkorea",
    max_jobs: int = 20,
) -> tuple[list[dict], str]:
    """선택한 실데이터 수집원을 사용하고, 필요하면 샘플로 검증한다."""
    if force_sample:
        return load_sample_jobs(project_root, search_keyword), "sample"
    if source == "jobkorea":
        return collect_jobkorea_jobs(search_keyword, max_jobs=max_jobs), "jobkorea"
    if source != "work24":
        raise ValueError(f"지원하지 않는 수집원입니다: {source}")
    api_key = os.environ.get("WORK24_API_KEY", "").strip()
    if api_key:
        return collect_work24_jobs(api_key, search_keyword=search_keyword), "work24"
    if require_live:
        raise Work24ConfigError(
            "실제 데이터 실행에는 WORK24_API_KEY가 필요합니다. 샘플 실행은 --require-live를 빼세요."
        )
    return load_sample_jobs(project_root, search_keyword), "sample"
