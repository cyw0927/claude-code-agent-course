"""AX 채용정보 Agent Pipeline 실행 진입점."""

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

from src.analyzer import analyze_jobs, filter_ax_related, find_new_jobs, save_job_history
from src.collector import collect_jobs
from src.gemini_client import summarize_with_gemini
from src.notifier import build_email_message, build_slack_payload, send_email, send_slack
from src.preprocess import build_dataframe, clean_jobs
from src.reporter import build_report_markdown, save_report

PROJECT_ROOT = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AX 채용정보 주간 파이프라인")
    parser.add_argument("--require-live", action="store_true", help="샘플 대체를 허용하지 않음")
    parser.add_argument("--sample", action="store_true", help="로컬 검증용 샘플 사용")
    parser.add_argument(
        "--source",
        choices=["jobkorea", "work24"],
        default=None,
        help="실데이터 수집원(기본: JOB_SOURCE 또는 jobkorea)",
    )
    parser.add_argument("--max-jobs", type=int, default=None, help="수집 건수(1~20)")
    parser.add_argument("--update-history", action="store_true", help="성공 후 신규 판별 기록 저장")
    parser.add_argument("--skip-gemini", action="store_true", help="Gemini 분석 생략")
    parser.add_argument("--skip-notifications", action="store_true", help="Slack/Gmail 발송 생략")
    return parser.parse_args()


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    args = parse_args()
    source_name = args.source or os.environ.get("JOB_SOURCE", "jobkorea")
    max_jobs = args.max_jobs or int(os.environ.get("JOBKOREA_MAX_JOBS", "20"))

    print("1) 채용공고 수집")
    if args.require_live and args.sample:
        raise SystemExit("--require-live와 --sample은 함께 사용할 수 없습니다.")
    jobs, source = collect_jobs(
        PROJECT_ROOT,
        search_keyword="AX",
        require_live=args.require_live,
        force_sample=args.sample,
        source=source_name,
        max_jobs=max_jobs,
    )
    print(f"   -> {len(jobs)}건 수집 (source={source})")

    print("2) 전처리 · 중복 제거")
    df_dedup = clean_jobs(build_dataframe(jobs))
    print(f"   -> {len(df_dedup)}건")

    print("3) 신규 공고 판별")
    history_path = PROJECT_ROOT / "data" / "processed" / "jobs_history.csv"
    new_jobs_df, existing_jobs_df, history_df = find_new_jobs(df_dedup, history_path)
    print(f"   -> 신규 {len(new_jobs_df)}건 / 기존 {len(existing_jobs_df)}건")

    print("4) 기본 분석 · AX 관련 필터링")
    stats = analyze_jobs(df_dedup, new_jobs_df, existing_jobs_df)
    ax_related_df = filter_ax_related(df_dedup)
    print(f"   -> AX/AI 관련 {len(ax_related_df)}건")

    print("5) Gemini 분석")
    gemini_results: list[dict] = []
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if gemini_api_key and not args.skip_gemini:
        gemini_results = summarize_with_gemini(ax_related_df.head(3).to_dict("records"), gemini_api_key)
        print(f"   -> {len(gemini_results)}건 응답 (사람 검증 필요)")
    else:
        print("   -> 키 없음 또는 --skip-gemini, 건너뜀")

    print("6) Markdown 보고서 생성")
    report_markdown = build_report_markdown(
        df_dedup, new_jobs_df, existing_jobs_df, ax_related_df, gemini_results, source=source
    )
    report_path = save_report(report_markdown, PROJECT_ROOT / "reports")
    print(f"   -> {report_path}")

    if args.update_history:
        save_job_history(df_dedup, history_df, history_path)
        print(f"7) 신규 판별 기록 저장 -> {history_path}")
    else:
        print("7) 신규 판별 기록 저장 안 함 (--update-history로 활성화)")

    if args.skip_notifications:
        print("8) 알림 발송 건너뜀")
    else:
        print("8) 알림 발송")
        slack_webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
        if slack_webhook_url:
            payload = build_slack_payload(
                report_path.stem[:10],
                {"total": stats["total"], "new": stats["new"], "ax_related": len(ax_related_df)},
                source,
            )
            response = send_slack(slack_webhook_url, payload)
            response.raise_for_status()
            print(f"   -> Slack 완료 ({response.status_code})")
        else:
            print("   -> Slack 키 없음, 건너뜀")

        gmail_user = os.environ.get("GMAIL_USER")
        gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD")
        if gmail_user and gmail_app_password:
            msg = build_email_message(report_markdown, report_path.stem[:10], gmail_user, gmail_user)
            send_email(msg, gmail_user, gmail_app_password)
            print("   -> Gmail 완료")
        else:
            print("   -> Gmail 키 없음, 건너뜀")
    print("완료")


if __name__ == "__main__":
    main()
