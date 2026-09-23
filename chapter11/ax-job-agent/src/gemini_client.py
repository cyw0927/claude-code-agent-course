"""Gemini API 연동. Notebook STEP 09에서 검증된 로직을 그대로 옮긴다.

주의: 여기서 만드는 해석은 AI가 생성한 참고 의견이며, 사람이 검증하지 않은 상태다.
STEP 10에서 같은 질문에도 모델/호출 시점에 따라 응답 품질이 달라지는 것을 실제로 확인했으므로,
이 모듈의 출력을 그대로 신뢰하지 말고 참고용으로만 사용해야 한다.
"""

import time

from google import genai
from google.genai import errors as genai_errors

# Notebook에서 실제로 검증된 모델명. gemini-2.5-flash(404)/gemini-3.6-flash·gemini-flash-latest
# (간헐적 503, 무료 등급 일일 한도 초과 429)를 거쳐 별도 쿼터를 쓰는 이 모델로 정착했다.
GEMINI_MODEL = "gemini-flash-lite-latest"


def build_prompt(row: dict) -> str:
    return (
        "다음은 채용공고의 일부 정보다. 원문 본문은 없고 아래 필드만 주어진다.\n"
        f"회사명: {row['company_name']}\n"
        f"공고 제목: {row['job_title']}\n"
        f"경력 조건: {row['career']}\n"
        f"근무 지역: {row['location']}\n\n"
        "위 정보만 근거로 답하라. 모르는 내용은 추측하지 말고 '정보 없음'이라고 써라.\n"
        "1) 직무 유형(한 단어 또는 짧은 구)\n"
        "2) AX(디지털 전환)/AI 관련성 설명 (1문장)\n"
        "3) 이 공고를 추천할 만한 이유 (1문장, 정보가 부족하면 '정보 없음'이라고 답하라)\n"
        "각 항목을 번호와 함께 한국어로 답하라."
    )


def _generate_with_retry(client, prompt: str, max_attempts: int = 4, base_delay: int = 5):
    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            return client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        except genai_errors.ServerError as e:
            last_error = e
            print(f"  (시도 {attempt}/{max_attempts}) 서버 오류, {base_delay}초 후 재시도: {e}")
            time.sleep(base_delay)
    raise last_error


def summarize_with_gemini(rows, api_key: str) -> list[dict]:
    """rows(공고 딕셔너리 리스트)를 Gemini에 보내 응답을 받는다. 각 요청은 실제 API 호출이다."""
    client = genai.Client(api_key=api_key)
    results = []
    for row in rows:
        prompt = build_prompt(row)
        response = _generate_with_retry(client, prompt)
        results.append({
            "company_name": row["company_name"],
            "job_title": row["job_title"],
            "gemini_response": response.text,
        })
    return results
