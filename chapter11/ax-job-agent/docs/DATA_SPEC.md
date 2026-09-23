# STEP 02. 채용공고 수집 데이터 명세

## 목표

검색 결과에서 안정적으로 확인할 수 있는 최소 정보만 수집한다.
DataFrame의 한 행은 채용공고 1건을 뜻한다.
상세 페이지의 모든 내용을 처음부터 수집하지 않는다.

## 초기 컬럼

| 컬럼 | 의미 | 초기 자료형 | 필수 여부 |
|---|---|---|---|
| `company_name` | 회사명 | string | 필수 |
| `job_title` | 공고 제목 | string | 필수 |
| `career` | 경력 조건 | string | 선택 |
| `location` | 근무 지역 | string | 선택 |
| `posted_date` | 등록일 원문 | string | 선택 |
| `closing_date` | 마감일 원문 | string | 선택 |
| `job_url` | 공고 URL | string | 필수 |
| `search_keyword` | 수집에 사용한 검색어 | string | 필수 |
| `collected_at` | 수집 시각 | datetime | 필수 |

날짜 원문은 먼저 문자열로 보존한다. 실제 표현을 확인한 뒤 별도의 전처리 STEP에서 날짜로 변환한다.

## 공고 식별 기준

기본 식별자는 `job_url`이다.

1. 이번 수집 결과에서 같은 `job_url`을 제거한다.
2. 지난 실행의 URL 목록과 비교한다.
3. 과거에 없던 URL만 신규 공고로 분류한다.

URL을 안정적으로 얻지 못할 때만 다음 조합을 보조 식별자로 검토한다.

```text
company_name + job_title + closing_date
```

## 결측치 원칙

- `company_name`, `job_title`, `job_url`이 없으면 정상 공고로 확정하지 않는다.
- `career`, `location`, 날짜가 없으면 빈 값을 유지하고 실제 결측 개수를 기록한다.
- 임의 문자열로 결측치를 채우기 전에 원본 HTML과 파싱 규칙을 확인한다.

## 수집 범위 확장 순서

1. 검색어 1개
2. 검색 결과 1페이지 접근
3. 공고 1건의 필드 확인
4. 공고 5~10건 수집
5. DataFrame 생성
6. 필요할 때만 검색어나 페이지 확대

## 자동 요청 전 확인

- 사이트 이용약관
- `robots.txt`
- HTTP 상태 코드
- 응답의 `Content-Type`
