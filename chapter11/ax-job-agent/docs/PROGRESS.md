# 현재 작업 진행 상황

기준일: 2026-09-23

## 완료된 구현

- STEP 01~09: 환경, 명세, 샘플 수집, 전처리, 신규 판별, 분석, Gemini 실제 호출
- STEP 11~16: Markdown 보고서, Slack/Gmail 모듈, `src/` 함수화, `main.py` 통합,
  샘플 8건을 사용한 로컬 전체 실행
- 잡코리아 공개 검색 결과 1페이지 수집기: 실제 페이지 구조에서 20건 파싱 확인
- 고용24 채용정보 Open API 연결도 선택 수집원으로 유지
- 실행 기록 누적: `--update-history` 사용 시 `jobs_history.csv` 갱신
- STEP 17~18 코드: 수동 실행과 매주 월요일 09:00 KST 예약을 가진 GitHub Actions workflow

## 실제 확인된 결과

- 프로젝트 venv: Python 3.14.7
- 샘플 8건 → 전처리 → 신규 판별 → AX/AI 필터 → Gemini 3건 → 보고서 저장 성공
- Slack/Gmail은 자격 증명이 없어 실제 발송하지 않았음
- 잡코리아 실제 AX 검색 결과 20건의 필드 추출 확인
- 잡코리아/고용24 파서는 오프라인 fixture 검사 완료

## 사용자 확인 또는 키가 필요한 항목

- STEP 10: Notebook의 `verification_df`에서 Gemini 결과에 대한 사람의 최종 판단
- 고용24를 선택할 경우: `WORK24_API_KEY`를 넣은 뒤 응답 확인
- STEP 12~13 실발송: Slack webhook 또는 Gmail 앱 비밀번호 등록 후 도착 확인
- STEP 17: GitHub에 workflow를 올리고 Actions에서 수동 실행 성공 확인
- STEP 18: 예약 실행은 workflow가 기본 브랜치에 반영된 다음 주기에 확인

이 항목들은 코드 미구현 상태가 아니라 외부 자격 증명이나 실제 도착 확인이 필요한 검증 단계다.

## 다음 실행

```powershell
Set-Location C:\dev\claude-code-agent-course\chapter11\ax-job-agent
.\.venv\Scripts\Activate.ps1

# 안전한 로컬 재검증: API 호출·알림 없음
python main.py --sample --skip-gemini --skip-notifications

# 실제 고용24 실행: .env에 키를 넣은 뒤
python main.py --require-live --update-history --skip-notifications
```

GitHub Actions에 필요한 secrets:

- AI 해석 사용 시: `GEMINI_API_KEY`
- 고용24 선택 시: `WORK24_API_KEY`
- 선택: `SLACK_WEBHOOK_URL`, `GMAIL_USER`, `GMAIL_APP_PASSWORD`

기본 수집원은 잡코리아 공개 검색 결과다. 로그인·회원·기업·상세 페이지에는 접근하지 않고,
검색 결과 1페이지만 한 번 요청해 최대 20건을 읽는다.
