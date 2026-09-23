# AX 채용정보 Agent Pipeline 진행표

이 문서는 Chapter 11 실습의 진행 순서와 각 단계의 완료 기준을 기록한다.
Notebook에서 실제 출력을 확인하기 전에는 해당 단계를 완료로 표시하지 않는다.

## 현재 상태

| STEP | 작업 | 상태 | 완료 기준 |
|---|---|---|---|
| 01 | 개발환경 확인 | 자동 실행 확인, 사용자 확인 대기 | Notebook에서 Python과 기본 패키지 버전 확인 |
| 02 | 수집 데이터 명세 | 완료 | 컬럼, 식별 기준, 결측 처리 원칙 검토 |
| 03 | 채용공고 페이지 접근 테스트 | 완료 (실크롤링 보류로 전환) | 약관·robots.txt 확인 후 상태 코드와 Content-Type 확인 |
| 04 | 소량 데이터 수집 | 완료 (샘플 데이터 기반) | 검색어 1개, 페이지 1개에서 공고 5~10개 확인 |
| 05 | DataFrame 생성 | 완료 | 명세 컬럼을 가진 DataFrame의 shape와 head 확인 |
| 06 | 전처리·중복 제거 | 완료 | 결측치와 URL 중복 처리 결과 확인 |
| 07 | 신규 공고 판별 | 완료 | 이전 URL 목록과 비교해 신규 공고만 분리 |
| 08 | 기본 분석·관련 공고 필터링 | 완료 | pandas 통계와 AX 관련 필터 결과 확인 |
| 09 | Gemini API 연동 | 완료 | 일부 공고에 대한 API 응답 확인 |
| 10 | Gemini 결과 검증 | HUMAN CHECK REQUIRED — 사용자 확인 대기 | 원문과 결과를 사람이 직접 비교 |
| 11 | Markdown 보고서 생성 | 완료 | 계산 사실과 Gemini 해석을 분리한 보고서 확인 |
| 12 | Slack 발송 | 코드 완료, 실발송 대기 | 테스트 메시지 도착과 한글 확인 |
| 13 | Gmail 발송 | 코드 완료, 실발송 대기 | 테스트 메일 도착과 본문 형식 확인 |
| 14 | 함수화 | 완료 | 검증된 Notebook 로직을 `src/`로 이동 |
| 15 | `main.py` 통합 | 완료 | 실행 순서만 연결하고 로직은 모듈에 유지 |
| 16 | 로컬 전체 실행 검증 | 완료 | `python main.py`가 끝까지 완료 |
| 17 | GitHub Actions 수동 실행 | workflow 완료, 원격 실행 대기 | `workflow_dispatch` 실행 성공 |
| 18 | GitHub Actions 주간 실행 | 예약 완료, 주기 검증 대기 | 한국시간 월요일 오전 9시 예약 확인 |

## STEP 01 실제 자동 실행 결과

2026-09-23에 프로젝트 가상환경으로 Notebook을 실행해 다음 출력을 확인했다.

- Python: 3.14.7
- pandas: 3.0.6
- requests: 2.34.2
- BeautifulSoup import: OK

VS Code에서 같은 `.venv` 커널을 선택한 뒤 사용자가 셀 출력을 직접 확인하면 STEP 01을 완료로 변경한다.

## STEP 03 실제 확인 결과

2026-09-23에 `https://www.jobkorea.co.kr/robots.txt`를 직접 조회했다 (Notebook 코드 셀로 재현, 실제 실행됨).

- status_code: 200
- Content-Type: text/plain
- robots.txt 안에 `ClaudeBot`, `anthropic-ai`, `Claude-Web`이 모두 포함되어 있으며, 해당 User-agent들은 `Disallow: /`로 사이트 전체가 차단 대상임을 확인

Claude 계열 에이전트가 자동으로 이 사이트를 수집하는 것은 사이트가 명시적으로 밝힌 의사에 반한다고 판단해, 사용자와 협의 후 잡코리아 실크롤링은 진행하지 않기로 결정했다. 채용공고 검색 결과 페이지(실제 콘텐츠) 요청은 하지 않았다.

## STEP 04 실제 확인 결과

실크롤링 대신 `data/raw/sample_jobs.html`(직접 작성한 가상의 채용공고 8건)을 BeautifulSoup으로 파싱해 확인했다 (Notebook에서 실제 실행).

- 파싱된 공고 수: 8건
- `career` 결측: 1건 (데이터브릿지 - 생성형 AI 프롬프트 엔지니어)
- `location` 결측: 1건 (넥스트웨이브 - AX 전환 PM)
- `company_name`, `job_title`, `job_url`은 8건 모두 정상 확인됨

이 결과는 샘플 데이터 기준이며, 실제 사이트 데이터는 형식이 다를 수 있다. 크롤링 소스가 정해지면 파싱 규칙을 다시 검증해야 한다.

## STEP 05 실제 확인 결과

`jobs` 리스트를 `DATA_SPEC.md` 컬럼 순서로 pandas DataFrame으로 변환해 확인했다 (Notebook에서 실제 실행).

- `shape`: `(8, 9)` — 공고 8건, 컬럼 9개
- `head()`: 8건 전부 컬럼 순서대로 정상 출력, 결측 필드(빈 문자열)도 그대로 보존됨
- `dtypes`: 전 컬럼이 `str`로 표시됨 (pandas 2.x에서 흔한 `object`가 아님 — pandas 3.0.6의 기본 문자열 dtype 변경으로 추정, 별도 확인 필요)

## STEP 06 실제 확인 결과

빈 문자열을 `pd.NA`로 통일하고, `job_url` 기준 중복 제거를 확인했다 (Notebook에서 실제 실행).

- 결측 개수: `career` 1건, `location` 1건, 나머지 컬럼 0건 (필수 컬럼 결측 0건)
- 실제 샘플 데이터의 `job_url` 중복: 0건 (8행 → 8행)
- 중복 제거 로직 자체 검증: 1건을 임의로 복제해 주입 → 9행 → 8행으로 정상 제거 확인

현재 샘플 데이터에는 실제 중복이 없어, 실제 수집 데이터로 전환하면 중복 제거 결과를 다시 확인해야 한다.

## STEP 07 실제 확인 결과

`data/processed/jobs_history.csv`(검증용으로 직접 작성)와 이번 실행 공고를 `job_url` 기준으로 비교했다 (Notebook에서 실제 실행).

- history 공고 수: 4건
- 이번 실행 전체 공고 수: 8건 → 신규 4건 / 기존 4건
- 신규 공고 목록(그린푸드, 데이터브릿지, 올바른회계법인, 넥스트웨이브)이 history에 없는 4건과 정확히 일치

`jobs_history.csv`는 실제 과거 실행 기록이 아니라 검증용 파일이다. 실제 운영 시 매 실행 후 히스토리 누적 로직이 별도로 필요하다(함수화 단계에서 정리 예정).

## STEP 08 실제 확인 결과

pandas로 기본 통계를 계산하고 `job_title` 키워드 기반 AX/AI 필터를 적용했다 (Notebook에서 실제 실행).

- 전체 공고 8건 (신규 4 / 기존 4), 회사별 공고 수는 전부 1건씩
- 지역/경력 결측 각 1건이 `NaN`으로 정상 집계됨, 검색어는 전부 `AX`
- `job_title`에 "AX" 또는 "AI"가 포함된 공고: 5건/8건

이 필터는 단순 문자열 포함 여부만 사용하는 규칙이며, 의미 기반 판단(오탐 검토 포함)은 STEP 09 Gemini 단계에서 다시 검토한다.

## STEP 09 실제 확인 결과

`google-genai` SDK로 실제 Gemini API를 호출했다 (Notebook에서 실제 실행, `.env`의 `GEMINI_API_KEY` 사용).

- 모델명 시행착오: `gemini-2.5-flash` → 404("no longer available to new users"), `gemini-3.6-flash`/`gemini-flash-latest` → 간헐적 503("high demand"), 반복 호출 후 `gemini-flash-latest`(내부적으로 `gemini-3.8-flash`)는 무료 등급 일일 한도(20회/day)로 429 RESOURCE_EXHAUSTED. 최종적으로 별도 쿼터를 쓰는 `gemini-flash-lite-latest`로 교체 + 재시도 로직(최대 4회, 5초 간격)을 적용해 안정적으로 응답 받음.
- AX/AI 관련 공고 5건 중 3건에 대해 실제 응답 수신: "직무 유형 / AX·AI 관련성 / 추천 이유" 3항목 형식으로 응답.
- 3건 모두 "추천 이유"는 "정보 없음"으로 답함 — 가진 정보(회사명/제목/경력/지역)만으로는 추천 근거를 만들지 않고 프롬프트 지시(정보 부족 시 정보 없음)를 따름.
- 1번 공고("AX 전략 기획 담당자")에 대해서는 "AX/AI 관련성 설명"도 "정보 없음"으로 답함 — 제목에 "AX"가 명시되어 있음에도 관련성을 설명하지 않아, 모델을 바꾸면 응답 품질이 균일하지 않을 수 있음을 실제로 확인했다. 이 부분이 STEP 10 사람 검증에서 특히 확인이 필요하다.
- `DATA_SPEC.md`가 상세 페이지 내용을 수집하지 않기로 했으므로, "요구 기술 추출"처럼 원문이 필요한 항목은 이번 단계에서 시도하지 않았다.

## STEP 10. Gemini 결과 검증 — HUMAN CHECK REQUIRED

Notebook에 `verification_df`(회사명/제목/경력/지역 + Gemini 응답 + 사람 확인 컬럼)를 만들어 두었다. 사용자가 직접 보고 판단해야 STEP 10이 완료된다. Claude가 자동으로 "검증 통과"로 표시하지 않는다. 특히 1번 공고의 "AX/AI 관련성: 정보 없음" 응답이 적절한지 확인이 필요하다.

## 버그 수정: Notebook 경로 계산이 실행 위치에 따라 깨지던 문제 (2026-09-23)

사용자가 VS Code에서 `ax_job_pipeline.ipynb`를 직접 열어 실행했을 때, STEP 04 "샘플 데이터 안내" 이후 코드 셀에서 `FileNotFoundError`가 발생했다.

- 원인: STEP 04/07/09 코드가 `Path.cwd().parent`로 프로젝트 루트를 추정했는데, 이는 Jupyter 커널의 cwd가 `notebooks/`일 때만 맞는 가정이었다. VS Code의 Jupyter 확장은 (설정에 따라) cwd를 프로젝트 루트(`ax-job-agent/`) 자체로 잡을 수 있고, 이 경우 `Path.cwd().parent`는 `chapter11/`이 되어 `data/raw/sample_jobs.html` 등을 찾지 못했다.
- 수정: `resolve_project_root()` 헬퍼를 추가해 `Path.cwd()`와 `Path.cwd().parent` 중 `data/`와 `requirements.txt`가 함께 있는 쪽을 프로젝트 루트로 판단하도록 바꿨다. STEP 04(`SAMPLE_HTML_PATH`), STEP 07(`HISTORY_PATH`), STEP 09(`ENV_PATH`)가 모두 이 `PROJECT_ROOT`를 사용하도록 통일했다.
- 검증: `nbclient`로 커널 cwd를 프로젝트 루트로 강제해 버그를 실제로 재현한 뒤, 수정 후 같은 조건에서 정상 실행되는 것을 확인했다 (`PROJECT_ROOT` 출력이 올바르게 `.../ax-job-agent`로 찍힘, 이후 STEP 결과도 기존과 동일).

## 진행 원칙

- 한 번에 한 STEP만 구현한다.
- 실제 출력과 예상 출력을 구분한다.
- Notebook 검증이 끝난 코드만 `src/`로 옮긴다.

## STEP 11~18 구현 결과

- 샘플 전체 실행으로 Markdown 보고서 저장까지 확인했다.
- Slack/Gmail 전송 코드는 준비됐으며 자격 증명이 없으면 건너뛴다.
- `src/` 모듈과 `main.py` 통합 후 샘플 8건 전체 실행을 완료했다.
- 고용24 Open API의 공식 `wanted` 필드를 데이터 명세에 연결했다.
- 잡코리아 공개 AX 검색 결과 1페이지에서 실제 공고 20건의 요약 필드를 확인하고 수집기를 연결했다.
- GitHub Actions는 수동 실행과 매주 월요일 09:00 KST 예약을 지원한다.
- 실제 고용24 호출, 알림 도착, Actions 성공 여부는 각 서비스의 키를 등록한 뒤 확인해야 한다.
