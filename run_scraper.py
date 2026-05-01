from __future__ import annotations

import argparse
import os

from app.workflows.pipeline import run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the car scraper pipeline.")
    parser.add_argument("start_url", help="Listing page URL to scrape.")
    parser.add_argument(
        "-o",
        "--output",
        default="cleaned.json",
        help="Output JSON file (default: cleaned.json)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of listings to process.",
    )
    parser.add_argument(
        "--gemini-api-key",
        default=os.getenv("GEMINI_API_KEY", ""),
        help="Gemini API key (defaults to GEMINI_API_KEY environment variable).",
    )
    parser.add_argument(
        "--gemini-model",
        default="gemini-3.1-flash-lite-preview",
        help="Gemini model name (default: gemini-3.1-flash-lite-preview).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    saved = run_pipeline(
        args.start_url,
        args.output,
        args.limit,
        gemini_api_key=args.gemini_api_key,
        gemini_model=args.gemini_model,
    )
    print(f"Saved {saved} listings to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
