# AX 채용정보 Agent Pipeline

고용24 Open API에서 AX 채용공고를 수집하고, pandas 전처리와 Gemini 요약을 거쳐
Markdown 보고서와 선택적 Slack/Gmail 알림을 만드는 Chapter 11 실습 프로젝트입니다.

## 로컬 실행

```powershell
Set-Location C:\dev\claude-code-agent-course\chapter11\ax-job-agent
.\.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
# .env에 필요한 키를 입력한 뒤:
python main.py --sample --skip-gemini --skip-notifications
```

키가 없으면 로컬 샘플 데이터로 파이프라인을 확인합니다. 실제 고용24 데이터만 허용하려면:

```powershell
python main.py --require-live --update-history --skip-notifications
```

주요 옵션:

- `--require-live`: `WORK24_API_KEY`가 없으면 실패
- `--sample`: 로컬 `.env`에 키가 있어도 검증용 샘플을 강제로 사용
- `--update-history`: 성공한 공고를 다음 실행의 신규 판별 기록에 저장
- `--skip-gemini`: Gemini 호출 생략
- `--skip-notifications`: Slack/Gmail 발송 생략

## 자동 실행

`.github/workflows/ax-job-agent.yml`은 매주 월요일 오전 9시(한국시간)에 실행됩니다.
GitHub 저장소의 **Settings → Secrets and variables → Actions**에 최소
`WORK24_API_KEY`와 `GEMINI_API_KEY`를 등록해야 합니다. Slack/Gmail 값은 선택입니다.
자동 실행은 실제 데이터 키가 없을 때 실패하며, 샘플 결과를 알림으로 보내지 않습니다.

보고서는 Actions 실행 화면의 `ax-job-weekly-report` artifact에서 받습니다.

## 문서

- [전체 진행표](docs/STEP_PLAN.md)
- [데이터 명세](docs/DATA_SPEC.md)
- [현재 진행 상황](docs/PROGRESS.md)
