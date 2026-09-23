# AX 채용정보 Agent Pipeline

Chapter 11 실습 프로젝트입니다.

## 현재 단계

STEP 08. 기본 분석 · AX 관련 공고 필터링 완료 (STEP 09 진입 전 대기 중)

- STEP 01 개발환경 확인: 자동 실행 확인 완료
- STEP 02 수집 데이터 명세: 완료
- STEP 03 채용공고 페이지 접근 테스트: 완료 (잡코리아 robots.txt가 `ClaudeBot`/`anthropic-ai`/`Claude-Web`을 전체 차단하고 있어, 실크롤링 대신 샘플 데이터 기반으로 전환하기로 결정)
- STEP 04 소량 데이터 수집: `data/raw/sample_jobs.html` 샘플로 공고 8건 파싱 확인
- STEP 05 DataFrame 생성: 완료
- STEP 06 전처리 · 중복 제거: 완료
- STEP 07 신규 공고 판별: `data/processed/jobs_history.csv`(검증용) 대비 신규 4건/기존 4건 확인
- STEP 08 기본 분석 · AX 관련 공고 필터링: pandas 통계 확인, AX/AI 키워드 필터로 5건/8건 확인

아직 하지 않는 것:

- 잡코리아(또는 다른 사이트) 실크롤링 — robots.txt 차단 문제로 보류 중, 별도 재검토 필요
- Gemini API — **STEP 09는 API Key 확보 후에만 진행** (현재 대기 중)
- Slack / Gmail
- GitHub Actions

## 로컬 작업 경로

```text
C:\\dev\\claude-code-agent-course
```

실습 브랜치: `ax-job-agent`

## 문서

- [전체 STEP 진행표](docs/STEP_PLAN.md)
- [채용공고 데이터 명세](docs/DATA_SPEC.md)
- [현재 작업 진행 상황](docs/PROGRESS.md)
