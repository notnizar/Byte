from __future__ import annotations

import argparse

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
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    saved = run_pipeline(args.start_url, args.output, args.limit)
    print(f"Saved {saved} listings to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
