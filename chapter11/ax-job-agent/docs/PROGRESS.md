# 현재 작업 진행 상황

이 문서는 2026-09-23 기준으로 실제 확인된 로컬 상태만 기록한다.
추정이나 예상 결과는 포함하지 않는다.

## 1. 현재 로컬 경로와 브랜치

- 로컬 경로: `C:\dev\claude-code-agent-course`
- 현재 브랜치: `ax-job-agent`
- `git status`: clean (커밋되지 않은 변경 없음)
- 브랜치 상태: `origin/ax-job-agent`와 동기화됨 (up to date)

## 2. origin과 upstream

- `origin`: https://github.com/cyw0927/claude-code-agent-course.git
- `upstream`: https://github.com/GilbertMoon/claude-code-agent-course.git

## 3. 완료한 Git 준비 작업

최근 커밋 6개 (최신순):

| 커밋 | 메시지 |
|---|---|
| `ed391c3` | docs: record chapter 11 setup and data spec |
| `fde4b66` | chore: sync chapter 11 branch with course |
| `572900a` | chore: sync fork with upstream course |
| `184ead5` | feat: add step 01 environment check notebook |
| `b03fd26` | docs: add chapter 11 step 01 guide |
| `ce52b9d` | chore: add step 01 dependencies |

즉, fork를 upstream과 동기화하고, `ax-job-agent` 브랜치를 만들어 STEP 01 관련 의존성·Notebook·문서를 커밋 및 origin에 push한 상태다.

## 4. STEP 01 환경 준비 상태

`docs/STEP_PLAN.md` 기준 STEP 01 상태: **"자동 실행 확인, 사용자 확인 대기"**

- Notebook (`notebooks/ax_job_pipeline.ipynb`) 자동 실행으로 출력은 이미 확인됨.
- 다만 VS Code에서 같은 `.venv` 커널을 선택한 뒤 사용자가 직접 셀 출력을 확인해야 STEP 01이 "완료"로 바뀐다. 현재는 그 사용자 확인이 아직 이루어지지 않았다.
- Notebook 마지막 셀("실행 결과 해석")은 아직 빈 템플릿 상태로, 사용자가 직접 채워야 한다.

## 5. 실제 확인된 Python과 패키지 버전

Notebook 실행 출력 기준:

- Python: `3.14.7`
- Platform: `Windows-11-10.0.26200-SP0`
- pandas: `3.0.6`
- requests: `2.34.2`
- BeautifulSoup import: `OK`

`requirements.txt`에 명시된 패키지: `pandas`, `requests`, `beautifulsoup4`, `jupyter`, `python-dotenv`

## 6. 현재 만들어진 문서와 Notebook

`chapter11/ax-job-agent/` 아래 실제 존재하는 파일 (`.venv` 제외):

- `README.md`
- `requirements.txt`
- `docs/STEP_PLAN.md` — 전체 18개 STEP 진행표
- `docs/DATA_SPEC.md` — STEP 02 채용공고 수집 데이터 명세 (초안)
- `notebooks/ax_job_pipeline.ipynb` — STEP 01 개발환경 확인 Notebook

## 7. STEP별 진행 기록 (2026-09-23)

### STEP 03. 채용공고 페이지 접근 테스트 — 완료 (실크롤링 대신 보류 결정)

- 작업 내용: `https://www.jobkorea.co.kr/robots.txt`를 Notebook 코드 셀에서 실제로 조회. `ClaudeBot`, `anthropic-ai`, `Claude-Web`이 `Disallow: /`로 전체 차단되어 있음을 확인. Claude 계열 에이전트가 이를 우회해 수집하는 것은 사이트가 명시한 의사에 반한다고 판단해, 사용자와 협의 후 잡코리아 실크롤링을 진행하지 않기로 결정.
- 수정 파일: `notebooks/ax_job_pipeline.ipynb` (STEP 03 셀 추가), `docs/STEP_PLAN.md`
- 실행 명령: Notebook 코드 셀 실행 (`requests.get(robots_url, ...)`, venv 내 `ax-job-agent` 커널 사용)
- 실제 결과: `status_code: 200`, `Content-Type: text/plain`, 3개 마커 모두 `True`
- 남은 문제: 채용공고 검색 결과 페이지(실제 콘텐츠) 요청은 하지 않았음. 크롤링 소스는 재검토 필요.
- HUMAN CHECK 필요 여부: 아니오 (사용자와 이미 협의 완료, 실행 결과는 자동 확인됨)
- 다음 STEP: STEP 04 (샘플 데이터 기반으로 대체)

### STEP 04. 소량 데이터 수집 (샘플 데이터 기반) — 완료

- 작업 내용: `data/raw/sample_jobs.html`(직접 작성한 가상의 채용공고 8건, 실제 사이트 데이터 아님)을 BeautifulSoup으로 파싱해 `DATA_SPEC.md` 컬럼 구조로 추출.
- 수정 파일: `data/raw/sample_jobs.html` (신규), `notebooks/ax_job_pipeline.ipynb` (STEP 04 셀 추가), `docs/STEP_PLAN.md`
- 실행 명령: Notebook 코드 셀 실행 (파싱 + 결측 확인)
- 실제 결과: 공고 8건 파싱 성공, `career` 결측 1건, `location` 결측 1건, `company_name`/`job_title`/`job_url`은 8건 모두 정상
- 남은 문제: 샘플 데이터 기준 결과이므로 실제 사이트 데이터의 형식(날짜 표기 등)과 다를 수 있음. 실제 크롤링 소스가 정해지면 파싱 규칙 재검증 필요.
- HUMAN CHECK 필요 여부: 아니오 (자동 실행으로 충분히 확인됨)
- 다음 STEP: STEP 05 (DataFrame 생성)

### STEP 05. DataFrame 생성 — 완료

- 작업 내용: STEP 04의 `jobs` 리스트를 `DATA_SPEC.md` 컬럼 순서(`company_name`~`collected_at`)로 pandas DataFrame으로 변환.
- 수정 파일: `notebooks/ax_job_pipeline.ipynb` (STEP 05 셀 추가), `docs/STEP_PLAN.md`
- 실행 명령: Notebook 코드 셀 실행 (`pd.DataFrame(jobs, columns=...)`, `df.shape`, `df.head(10)`, `df.dtypes`)
- 실제 결과: `shape: (8, 9)`, `head()` 8건 정상 출력(결측 필드도 빈 문자열로 보존), `dtypes`는 전 컬럼 `str`
- 남은 문제: `dtypes`가 `object`가 아니라 `str`로 나온 것은 pandas 3.0.6의 기본 문자열 dtype 변경으로 추정되며 아직 별도로 확인하지 않음. `career`/`location`의 빈 문자열을 STEP 06에서 결측치로 통일할지 결정 필요.
- HUMAN CHECK 필요 여부: 아니오 (자동 실행으로 충분히 확인됨)
- 다음 STEP: STEP 06 (전처리·중복 제거)

### STEP 06. 전처리 · 중복 제거 — 완료

- 작업 내용: `career`/`location`의 빈 문자열을 `pd.NA`로 통일(임의 문자열 채움이 아님). `job_url` 기준 중복 검사·제거 로직 적용. 실제 샘플에는 중복이 없어, 1건을 임의로 복제해 주입한 별도 검증으로 `drop_duplicates`가 실제로 동작함을 확인.
- 수정 파일: `notebooks/ax_job_pipeline.ipynb` (STEP 06 셀 추가), `docs/STEP_PLAN.md`
- 실행 명령: Notebook 코드 셀 실행 (`df.replace("", pd.NA)`, `isna().sum()`, `duplicated()`, `drop_duplicates()`)
- 실제 결과: 결측 `career` 1건/`location` 1건(필수 컬럼 결측 0건), 실제 샘플 job_url 중복 0건(8→8), 중복 주입 검증 9→8행으로 정상 제거
- 남은 문제: 실제 중복이 있는 데이터로 검증한 적은 없음. 크롤링 소스가 정해지면 다시 확인 필요.
- HUMAN CHECK 필요 여부: 아니오 (자동 실행으로 충분히 확인됨)
- 다음 STEP: STEP 07 (신규 공고 판별)

### STEP 07. 신규 공고 판별 — 완료

- 작업 내용: `data/processed/jobs_history.csv`(검증용으로 직접 작성, 공고 4건)를 읽어 이번 실행 8건과 `job_url` 기준으로 비교. 신규/기존 공고를 분리.
- 수정 파일: `data/processed/jobs_history.csv` (신규), `notebooks/ax_job_pipeline.ipynb` (STEP 07 셀 추가), `docs/STEP_PLAN.md`
- 실행 명령: Notebook 코드 셀 실행 (`pd.read_csv`, `isin` 기반 비교)
- 실제 결과: history 4건, 이번 실행 8건 중 신규 4건/기존 4건. 신규 목록이 history에 없는 4건과 정확히 일치.
- 남은 문제: `jobs_history.csv`는 검증용 파일. 실제 운영 시 매 실행 후 히스토리를 누적 반영하는 로직이 필요(함수화 단계에서 정리 예정).
- HUMAN CHECK 필요 여부: 아니오 (자동 실행으로 충분히 확인됨)
- 다음 STEP: STEP 08 (기본 분석·AX 관련 공고 필터링)

### STEP 08. 기본 분석 · AX 관련 공고 필터링 — 완료

- 작업 내용: pandas `value_counts()`로 회사별/지역별/경력별/검색어별 공고 수 집계. `job_title`에 "AX" 또는 "AI" 문자열이 포함되는지로 단순 키워드 필터 적용.
- 수정 파일: `notebooks/ax_job_pipeline.ipynb` (STEP 08 셀 추가), `docs/STEP_PLAN.md`
- 실행 명령: Notebook 코드 셀 실행 (`value_counts()`, `str.contains()`)
- 실제 결과: 전체 8건(신규 4/기존 4), 지역/경력 결측 각 1건이 `NaN`으로 집계, 검색어는 전부 `AX`, AX/AI 키워드 포함 공고 5건/8건
- 남은 문제: 지금 필터는 단순 문자열 포함 여부라 오탐 가능성이 있음. STEP 09 Gemini 단계에서 의미 기반으로 재검토 필요.
- HUMAN CHECK 필요 여부: 아니오 (자동 실행으로 충분히 확인됨)
- 다음 STEP: STEP 09 (Gemini API 연동) — **API Key 필요, 진입 전 사용자 확인 필요**

### 환경 관련 특이사항 — Notebook 실행 방법

이 로컬 환경에서는 `jupyter nbconvert --execute` (CLI)가 Windows 애플리케이션 제어 정책에 의해 차단된다(`[WinError 4551] 애플리케이션 제어 정책에서 이 파일을 차단했습니다`). 대신 `nbclient.NotebookClient`를 Python 스크립트에서 직접 호출하는 방식은 정상 동작한다. 또한 기본 `python3` 커널스펙은 PATH의 다른 Python(3.12)을 가리키므로, 프로젝트 venv에 바인딩된 전용 커널(`ax-job-agent`)을 등록해 사용했다. 자세한 명령은 9번 항목 참고.

## 8. 아직 하지 않은 작업

`docs/STEP_PLAN.md` 기준 STEP 09~18은 모두 "대기" 상태다.
- STEP 09~10: Gemini API 연동 및 검증 — 미착수 (API Key 필요, 도달 시 반드시 확인 요청)
- STEP 11: Markdown 보고서 생성 — 미착수
- STEP 12~13: Slack/Gmail 발송 — 미착수 (실제 발송 직전 반드시 확인 요청)
- STEP 14~16: 함수화, `main.py` 통합, 로컬 전체 실행 검증 — 미착수
- STEP 17~18: GitHub Actions 수동/주간 실행 — 미착수 (원격 push 필요 시점에 반드시 확인 요청)
- 실크롤링 코드는 작성하지 않았고, 현재는 샘플 데이터(`data/raw/sample_jobs.html`) 기반으로만 진행 중.
- STEP 01은 자동 실행 확인까지만 완료, VS Code에서 사용자가 직접 셀을 확인하는 절차는 아직 남아있음(HUMAN CHECK REQUIRED, 선택 사항 — 진행 자체를 막지는 않음).

## 9. 다음 시작 위치

1. **STEP 09(Gemini API 연동) 진입 전 반드시 사용자에게 API Key 확보 여부를 먼저 확인한다 (HUMAN CHECK / 정지 조건).** Gemini는 STEP 09 이전에는 설치·구현하지 않는다는 원칙을 지켰다.
2. API Key가 준비되면 `.env`(gitignore 대상)에 `GEMINI_API_KEY`를 넣고, 저장소에는 `.env.example`만 추가한다.
3. 여유가 있을 때 사용자가 VS Code에서 Notebook을 열어 `ax-job-agent` 커널로 전체 셀을 한 번 눈으로 확인하면 STEP 01의 HUMAN CHECK 항목도 함께 정리된다.

## 10. 작업을 다시 시작할 때 사용할 PowerShell 명령

```powershell
Set-Location C:\dev\claude-code-agent-course
git status
git checkout ax-job-agent
git pull origin ax-job-agent

Set-Location chapter11\ax-job-agent
.\.venv\Scripts\Activate.ps1
```

VS Code에서 열 경우:

```powershell
code C:\dev\claude-code-agent-course\chapter11\ax-job-agent
```

Notebook을 열고 커널 선택에서 **`Python (ax-job-agent venv)`** (커널 이름 `ax-job-agent`, 프로젝트 venv에 직접 바인딩됨)을 지정한 뒤 셀을 직접 실행해 확인한다. 이 커널이 목록에 없다면 아래 명령으로 다시 등록한다.

```powershell
.\.venv\Scripts\python.exe -m ipykernel install --user --name=ax-job-agent --display-name="Python (ax-job-agent venv)"
```

Notebook을 CLI에서 자동 실행해야 할 경우, `jupyter nbconvert --execute`는 이 환경에서 차단되므로 아래처럼 `nbclient`를 직접 호출한다.

```powershell
.\.venv\Scripts\python.exe -c "
import nbformat
from nbclient import NotebookClient
nb = nbformat.read('notebooks/ax_job_pipeline.ipynb', as_version=4)
client = NotebookClient(nb, timeout=60, kernel_name='ax-job-agent', resources={'metadata': {'path': 'notebooks'}})
client.execute()
nbformat.write(nb, 'notebooks/ax_job_pipeline.ipynb')
print('SAVED')
"
```
