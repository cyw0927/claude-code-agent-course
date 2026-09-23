"""고용24 채용정보 Open API 클라이언트."""

import os
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, Optional

WORK24_ENDPOINT = "https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo210L01.do"

DATA_SPEC_COLUMNS = [
    "company_name", "job_title", "career", "location", "posted_date",
    "closing_date", "job_url", "search_keyword", "collected_at",
]

WORK24_FIELD_MAP = {
    "company_name": "company",
    "job_title": "title",
    "career": "career",
    "location": "region",
    "posted_date": "regDt",
    "closing_date": "closeDt",
    "job_url": "wantedInfoUrl",
}


class Work24ConfigError(RuntimeError):
    """고용24 API 설정이 없거나 잘못됐을 때 발생한다."""


class Work24ResponseError(RuntimeError):
    """고용24 API가 사용할 수 없는 응답을 반환했을 때 발생한다."""


def get_api_key() -> str:
    api_key = os.environ.get("WORK24_API_KEY", "").strip()
    if not api_key:
        raise Work24ConfigError(
            "WORK24_API_KEY가 없습니다. .env 또는 GitHub Actions secret에 인증키를 설정하세요."
        )
    return api_key


def build_request_params(
    api_key: str,
    start_page: int = 1,
    display: int = 100,
    keyword: str | None = None,
) -> dict[str, Any]:
    if start_page < 1 or start_page > 1000:
        raise ValueError("start_page는 1~1000이어야 합니다.")
    if display < 1 or display > 100:
        raise ValueError("display는 1~100이어야 합니다.")
    params: dict[str, Any] = {
        "authKey": api_key,
        "callTp": "L",
        "returnType": "XML",
        "startPage": start_page,
        "display": display,
    }
    if keyword:
        params["keyword"] = keyword
    return params


def fetch_job_listings_xml(
    api_key: Optional[str] = None,
    start_page: int = 1,
    display: int = 100,
    keyword: str | None = None,
    timeout: int = 20,
):
    """고용24 채용목록 XML을 요청한다."""
    import requests

    key = api_key or get_api_key()
    params = build_request_params(key, start_page, display, keyword)
    return requests.get(WORK24_ENDPOINT, params=params, timeout=timeout)


def check_response(response) -> None:
    response.raise_for_status()
    if not response.text.strip():
        raise Work24ResponseError("고용24 API가 빈 응답을 반환했습니다.")
    content_type = response.headers.get("Content-Type", "").lower()
    if "xml" not in content_type and not response.text.lstrip().startswith("<?xml"):
        raise Work24ResponseError(
            f"고용24 API 응답이 XML이 아닙니다(Content-Type={content_type or '없음'})."
        )


def parse_job_records(xml_text: str, record_tag: str = "wanted") -> list[dict[str, str]]:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise Work24ResponseError(f"고용24 XML 파싱 실패: {exc}") from exc
    return [
        {child.tag: (child.text or "").strip() for child in record_elem}
        for record_elem in root.iter(record_tag)
    ]


def map_to_data_spec(
    raw_record: dict[str, str],
    field_map: dict[str, str] = WORK24_FIELD_MAP,
    search_keyword: str = "AX",
) -> dict[str, str]:
    result: dict[str, str] = {}
    for column in DATA_SPEC_COLUMNS:
        if column == "search_keyword":
            result[column] = search_keyword
        elif column == "collected_at":
            result[column] = datetime.now().isoformat(timespec="seconds")
        else:
            result[column] = raw_record.get(field_map.get(column, ""), "")
    return result


def collect_work24_jobs(
    api_key: str | None = None,
    search_keyword: str = "AX",
    start_page: int = 1,
    display: int = 100,
) -> list[dict[str, str]]:
    response = fetch_job_listings_xml(api_key, start_page, display, search_keyword)
    check_response(response)
    records = parse_job_records(response.text)
    if not records:
        raise Work24ResponseError(
            "고용24 응답에 채용공고(wanted)가 없습니다. 인증키와 검색 조건을 확인하세요."
        )
    return [map_to_data_spec(record, search_keyword=search_keyword) for record in records]


if __name__ == "__main__":
    fixture = """<?xml version="1.0"?><wantedRoot><wanted>
    <company>테스트컴퍼니</company><title>AX 엔지니어</title><career>경력무관</career>
    <region>서울</region><regDt>20260923</regDt><closeDt>20261031</closeDt>
    <wantedInfoUrl>https://example.com/job/1</wantedInfoUrl></wanted></wantedRoot>"""
    mapped = map_to_data_spec(parse_job_records(fixture)[0], search_keyword="AX")
    assert mapped["company_name"] == "테스트컴퍼니"
    assert mapped["job_url"] == "https://example.com/job/1"
    print("고용24 XML 파서 자체 검사 통과")
