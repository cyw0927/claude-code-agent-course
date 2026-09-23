"""Markdown 주간 보고서 생성. Notebook STEP 11에서 검증된 로직을 그대로 옮긴다.

pandas가 계산한 사실(1~2번 섹션)과 Gemini 해석(3번 섹션)을 명확히 구분한다.
"""

from datetime import datetime
from pathlib import Path

import pandas as pd


def build_report_markdown(
    df_dedup: pd.DataFrame,
    new_jobs_df: pd.DataFrame,
    existing_jobs_df: pd.DataFrame,
    ax_related_df: pd.DataFrame,
    gemini_results: list[dict],
    source: str = "sample",
    report_date: str | None = None,
) -> str:
    report_date = report_date or datetime.now().strftime("%Y-%m-%d")
    gemini_by_key = {(r["company_name"], r["job_title"]): r["gemini_response"] for r in gemini_results}

    # 이번 실행에서 "AX/AI 관련성 설명"이 부실했던 응답이 있는지 매번 다시 검사한다
    # (하드코딩된 특정 사례를 주의사항에 박아두면 다음 실행에서 응답이 바뀔 때 본문과 모순될 수 있다).
    suspect_entries = []
    for key, resp in gemini_by_key.items():
        resp_lines = resp.strip().splitlines()
        relevance_line = next((line for line in resp_lines if line.strip().startswith("2)")), "")
        if "정보 없음" in relevance_line:
            suspect_entries.append(key)

    lines = []
    lines.append("# 주간 AX 채용 동향")
    lines.append("")
    lines.append(f"실행일: {report_date}")
    lines.append("")

    lines.append("## 1. 이번 주 요약")
    lines.append("")
    lines.append(f"- 전체 공고 수: {len(df_dedup)}건")
    lines.append(f"- 신규 공고 수: {len(new_jobs_df)}건")
    lines.append(f"- 기존 공고 수: {len(existing_jobs_df)}건")
    lines.append(f"- AX/AI 관련 공고 수: {len(ax_related_df)}건 (job_title 키워드 기준)")
    lines.append("")

    lines.append("## 2. 주요 동향 (pandas 계산 사실)")
    lines.append("")
    lines.append("### 회사별 공고 수")
    lines.append("")
    for company, count in df_dedup["company_name"].value_counts().items():
        lines.append(f"- {company}: {count}건")
    lines.append("")
    lines.append("### 지역별 공고 수")
    lines.append("")
    for location, count in df_dedup["location"].value_counts(dropna=False).items():
        label = location if pd.notna(location) else "(미기재)"
        lines.append(f"- {label}: {count}건")
    lines.append("")
    lines.append("### 경력 조건별 공고 수")
    lines.append("")
    for career, count in df_dedup["career"].value_counts(dropna=False).items():
        label = career if pd.notna(career) else "(미기재)"
        lines.append(f"- {label}: {count}건")
    lines.append("")

    lines.append("## 3. 추천 공고 (AX/AI 관련, Gemini 해석 포함)")
    lines.append("")
    for _, row in ax_related_df.iterrows():
        key = (row["company_name"], row["job_title"])
        lines.append(f"### {row['company_name']} - {row['job_title']}")
        lines.append("")
        career_label = row["career"] if pd.notna(row["career"]) else "(미기재)"
        location_label = row["location"] if pd.notna(row["location"]) else "(미기재)"
        lines.append(f"- 경력: {career_label}")
        lines.append(f"- 지역: {location_label}")
        lines.append(f"- 링크: {row['job_url']}")
        lines.append("")
        if key in gemini_by_key:
            lines.append("**Gemini 해석 (참고용, 사람 검증 미완료):**")
            lines.append("")
            lines.append("```")
            lines.append(gemini_by_key[key])
            lines.append("```")
        else:
            lines.append("_Gemini 분석 대상에 포함되지 않음_")
        lines.append("")

    lines.append("## 4. 데이터 기준")
    lines.append("")
    if len(df_dedup) > 0:
        lines.append(f"- 수집 시각: {df_dedup['collected_at'].iloc[0]}")
    source_label = {
        "work24": "고용24 채용정보 Open API",
        "jobkorea": "잡코리아 공개 검색 결과 1페이지",
        "sample": "로컬 검증용 sample_jobs.html (가상 데이터)",
    }.get(source, source)
    lines.append(f"- 데이터 출처: {source_label}")
    lines.append("")

    lines.append("## 5. 주의사항")
    lines.append("")
    lines.append("- 1~2번(전체/신규/기존 공고 수, 회사별/지역별/경력별 통계)은 pandas가 계산한 사실이다.")
    lines.append(
        "- 3번의 Gemini 해석은 AI가 생성한 참고 의견이며 사람이 검증하지 않았다. "
        "같은 질문이라도 모델/호출 시점에 따라 응답 품질이 달라질 수 있음을 실제로 확인했다. "
        "이 해석을 그대로 신뢰하지 말고 참고용으로만 사용해야 한다."
    )
    if suspect_entries:
        suspect_list = ", ".join(f"{c}({t})" for c, t in suspect_entries)
        lines.append(f"- **이번 실행에서** 다음 응답이 관련성 설명을 '정보 없음'으로 답해 재검토가 필요하다: {suspect_list}")
    else:
        lines.append("- 이번 실행에서는 관련성 설명이 '정보 없음'으로 나온 응답이 없었다 (그렇다고 나머지 해석이 검증되었다는 뜻은 아니다).")

    return "\n".join(lines)


def save_report(markdown_text: str, reports_dir: Path, report_date: str | None = None) -> Path:
    report_date = report_date or datetime.now().strftime("%Y-%m-%d")
    reports_dir.mkdir(exist_ok=True)
    report_path = reports_dir / f"{report_date}-ax-job-weekly-report.md"
    report_path.write_text(markdown_text, encoding="utf-8")
    return report_path
