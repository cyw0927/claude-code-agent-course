import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.jobkorea_client import canonical_job_url, parse_jobkorea_jobs  # noqa: E402


FIXTURE = """
<div class="flex w-full gap-5 p-7">
  <div class="w-full">
    <div><a data-sentry-component="Title"
      href="https://www.jobkorea.co.kr/Recruit/GI_Read/50032017?logpath=1">
      AX 컨설턴트 채용
    </a></div>
    <span><a><span class="text-typo-b2-16">테스트회사</span></a></span>
    <span class="text-typo-b4-14">서울 강남구</span>
    <span class="flex-shrink-0 text-gray700 text-typo-c1-13">경력3년↑</span>
    <span class="text-gray700 text-typo-c1-13">09/21(월) 등록</span>
    <span class="text-typo-c1-13 text-gray700">10/01(목) 마감</span>
  </div>
</div>
"""


class JobKoreaClientTest(unittest.TestCase):
    def test_parse_public_search_card(self):
        job = parse_jobkorea_jobs(FIXTURE, max_jobs=1)[0]
        self.assertEqual(job["company_name"], "테스트회사")
        self.assertEqual(job["job_title"], "AX 컨설턴트 채용")
        self.assertEqual(job["career"], "경력3년↑")
        self.assertEqual(job["location"], "서울 강남구")
        self.assertEqual(job["posted_date"], "09/21(월)")
        self.assertEqual(job["closing_date"], "10/01(목)")
        self.assertEqual(
            job["job_url"],
            "https://www.jobkorea.co.kr/Recruit/GI_Read/50032017",
        )

    def test_canonical_url_removes_tracking_query(self):
        self.assertEqual(
            canonical_job_url("https://example.com/job/1?tracking=yes#top"),
            "https://example.com/job/1",
        )

    def test_maximum_is_limited_to_one_page(self):
        with self.assertRaises(ValueError):
            parse_jobkorea_jobs(FIXTURE, max_jobs=21)


if __name__ == "__main__":
    unittest.main()
