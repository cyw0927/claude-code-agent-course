"""Slack / Gmail 발송. Notebook STEP 12~13에서 검증된 로직을 그대로 옮긴다.

이 모듈의 send_slack()/send_email()은 실제로 메시지를 보낸다. 자격 증명(SLACK_WEBHOOK_URL,
GMAIL_USER/GMAIL_APP_PASSWORD)이 설정되어 있지 않으면 main.py에서 호출을 건너뛴다.
"""

import smtplib
from email.mime.text import MIMEText

import requests


def build_slack_payload(report_date: str, summary_stats: dict, source: str) -> dict:
    text_lines = [
        f"*주간 AX 채용 동향* ({report_date})",
        f"- 전체 공고 수: {summary_stats['total']}건",
        f"- 신규 공고 수: {summary_stats['new']}건",
        f"- AX/AI 관련 공고 수: {summary_stats['ax_related']}건",
        f"- 데이터 출처: {source}",
        "- 전체 보고서는 이번 실행의 GitHub Actions artifact에서 확인하세요.",
    ]
    return {"text": "\n".join(text_lines)}


def send_slack(webhook_url: str, payload: dict, timeout: int = 10) -> requests.Response:
    return requests.post(webhook_url, json=payload, timeout=timeout)


def build_email_message(report_markdown: str, report_date: str, to_addr: str, from_addr: str) -> MIMEText:
    msg = MIMEText(report_markdown, _charset="utf-8")
    msg["Subject"] = f"주간 AX 채용 동향 ({report_date})"
    msg["From"] = from_addr
    msg["To"] = to_addr
    return msg


def send_email(msg: MIMEText, gmail_user: str, gmail_app_password: str) -> None:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
        server.login(gmail_user, gmail_app_password)
        server.send_message(msg)
