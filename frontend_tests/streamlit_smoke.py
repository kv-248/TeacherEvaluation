from __future__ import annotations

import argparse
import sys
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


DEFAULT_APP_URL = "http://127.0.0.1:8501"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke test the Streamlit coaching report frontend.")
    parser.add_argument("--app-url", default=DEFAULT_APP_URL, help="Streamlit app URL.")
    parser.add_argument("--headed", action="store_true", help="Run Chromium headed instead of headless.")
    parser.add_argument("--timeout-ms", type=int, default=30_000, help="Per-check timeout in milliseconds.")
    parser.add_argument("--screenshot", type=Path, default=None, help="Optional screenshot path.")
    return parser.parse_args()


def _expect_heading(page, name: str, timeout_ms: int) -> None:
    page.get_by_role("heading", name=name).wait_for(state="visible", timeout=timeout_ms)


def main() -> int:
    args = _parse_args()

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=not args.headed)
            context = browser.new_context(viewport={"width": 1440, "height": 1200})
            page = context.new_page()
            page.goto(args.app_url, wait_until="networkidle", timeout=args.timeout_ms)

            _expect_heading(page, "TeacherEvaluation", args.timeout_ms)
            _expect_heading(page, "No Material Intervention Needed", args.timeout_ms)
            _expect_heading(page, "Strengths to Preserve", args.timeout_ms)
            _expect_heading(page, "Strength Inventory", args.timeout_ms)
            _expect_heading(page, "Additional Observation Inventory", args.timeout_ms)
            _expect_heading(page, "Low-Confidence Watchlist", args.timeout_ms)

            page.get_by_role("button", name="Download JSON").wait_for(state="visible", timeout=args.timeout_ms)
            page.get_by_role("button", name="Download Markdown").wait_for(state="visible", timeout=args.timeout_ms)

            if args.screenshot is not None:
                args.screenshot.parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(args.screenshot), full_page=True)

            context.close()
            browser.close()
    except PlaywrightTimeoutError as exc:
        print(f"Streamlit smoke test timed out: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Streamlit smoke test failed: {exc}", file=sys.stderr)
        return 1

    print("Streamlit smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
