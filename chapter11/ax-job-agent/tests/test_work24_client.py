import os
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.work24_client import (  # noqa: E402
    DATA_SPEC_COLUMNS,
    Work24ConfigError,
    build_request_params,
    get_api_key,
    map_to_data_spec,
    parse_job_records,
)


class Work24ClientTest(unittest.TestCase):
    def test_official_xml_mapping(self):
        xml = """<?xml version="1.0"?><wantedRoot><wanted>
        <company>회사</company><title>AX 개발자</title><career>신입</career>
        <region>서울</region><regDt>20260923</regDt><closeDt>20261001</closeDt>
        <wantedInfoUrl>https://example.com/1</wantedInfoUrl></wanted></wantedRoot>"""
        mapped = map_to_data_spec(parse_job_records(xml)[0], search_keyword="AX")
        self.assertEqual(mapped["company_name"], "회사")
        self.assertEqual(mapped["job_url"], "https://example.com/1")
        self.assertEqual(set(mapped), set(DATA_SPEC_COLUMNS))

    def test_request_limits_and_keyword(self):
        params = build_request_params("key", start_page=1, display=100, keyword="AX")
        self.assertEqual(params["keyword"], "AX")
        with self.assertRaises(ValueError):
            build_request_params("key", display=101)

    def test_missing_key_fails_before_request(self):
        previous = os.environ.pop("WORK24_API_KEY", None)
        try:
            with self.assertRaises(Work24ConfigError):
                get_api_key()
        finally:
            if previous is not None:
                os.environ["WORK24_API_KEY"] = previous


if __name__ == "__main__":
    unittest.main()
