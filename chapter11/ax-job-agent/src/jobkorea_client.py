"""잡코리아 공개 검색 결과 1페이지 수집기.

로그인·상세 페이지에는 접근하지 않고 공개 검색 결과에 표시된 요약 정보만 읽는다.
한 번 실행할 때 요청 1회, 최대 20건으로 제한한다.
"""

import re
import urllib.robotparser
from datetime import datetime
from urllib.parse import urlsplit, urlunsplit

JOBKOREA_SEARCH_URL = "https://www.jobkorea.co.kr/Search/"
JOBKOREA_ROBOTS_URL = "https://www.jobkorea.co.kr/robots.txt"
USER_AGENT = (
    "AXJobAgent/1.0 "
    "(+https://github.com/cyw0927/claude-code-agent-course; public-search-only)"
)


class JobKoreaError(RuntimeError):
    """잡코리아 공개 검색 결과를 사용할 수 없을 때 발생한다."""


def canonical_job_url(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def _find_card(anchor):
    current = anchor
    required = {"flex", "w-full", "gap-5", "p-7"}
    while current is not None:
        if required.issubset(set(current.get("class", []))):
            return current
        current = current.parent
    return None


def parse_jobkorea_jobs(
    html: str,
    search_keyword: str = "AX",
    max_jobs: int = 20,
) -> list[dict[str, str]]:
    """렌더링된 공개 검색 HTML을 공통 데이터 명세로 변환한다."""
    from bs4 import BeautifulSoup

    if max_jobs < 1 or max_jobs > 20:
        raise ValueError("max_jobs는 1~20이어야 합니다.")

    soup = BeautifulSoup(html, "html.parser")
    collected_at = datetime.now().isoformat(timespec="seconds")
    jobs: list[dict[str, str]] = []

    for anchor in soup.select('a[data-sentry-component="Title"]'):
        card = _find_card(anchor)
        if card is None:
            continue

        company_tag = card.select_one("span.text-typo-b2-16")
        location_tags = card.select("span.text-typo-b4-14")
        career_tag = card.select_one("span.flex-shrink-0.text-typo-c1-13")
        small_texts = [
            tag.get_text(" ", strip=True)
            for tag in card.select("span.text-typo-c1-13")
        ]
        posted = next((text for text in small_texts if text.endswith("등록")), "")
        closing = next(
            (
                text
                for text in small_texts
                if text.endswith("마감") or text == "상시채용"
            ),
            "",
        )

        job_url = canonical_job_url(anchor.get("href", ""))
        company_name = company_tag.get_text(" ", strip=True) if company_tag else ""
        job_title = anchor.get_text(" ", strip=True)
        if not (company_name and job_title and job_url):
            continue

        jobs.append({
            "company_name": company_name,
            "job_title": job_title,
            "career": career_tag.get_text(" ", strip=True) if career_tag else "",
            "location": location_tags[0].get_text(" ", strip=True) if location_tags else "",
            "posted_date": re.sub(r"\s*등록$", "", posted),
            "closing_date": re.sub(r"\s*마감$", "", closing),
            "job_url": job_url,
            "search_keyword": search_keyword,
            "collected_at": collected_at,
        })
        if len(jobs) >= max_jobs:
            break

    if not jobs:
        raise JobKoreaError(
            "잡코리아 검색 결과를 찾지 못했습니다. 페이지 구조 또는 접근 상태를 확인하세요."
        )
    return jobs


def _robots_allows(session, search_url: str, timeout: int) -> bool:
    response = session.get(
        JOBKOREA_ROBOTS_URL,
        headers={"User-Agent": USER_AGENT},
        timeout=timeout,
    )
    response.raise_for_status()
    parser = urllib.robotparser.RobotFileParser()
    parser.set_url(JOBKOREA_ROBOTS_URL)
    parser.parse(response.text.splitlines())
    return parser.can_fetch(USER_AGENT, search_url)


def collect_jobkorea_jobs(
    search_keyword: str = "AX",
    max_jobs: int = 20,
    timeout: int = 20,
) -> list[dict[str, str]]:
    """공개 검색 결과 1페이지를 요청하고 최대 20건을 반환한다."""
    import requests

    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept-Language": "ko-KR,ko;q=0.9",
    })
    prepared = requests.Request(
        "GET",
        JOBKOREA_SEARCH_URL,
        params={"stext": search_keyword, "tabType": "recruit"},
    ).prepare()
    search_url = prepared.url
    if not _robots_allows(session, search_url, timeout):
        raise JobKoreaError("현재 robots.txt 규칙에서 공개 검색 페이지 수집을 허용하지 않습니다.")

    response = session.get(
        JOBKOREA_SEARCH_URL,
        params={"stext": search_keyword, "tabType": "recruit"},
        timeout=timeout,
    )
    response.raise_for_status()
    return parse_jobkorea_jobs(response.text, search_keyword, max_jobs)
