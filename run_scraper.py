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
    parser.add_argument(
        "--no-scan-llm",
        action="store_true",
        help="Disable Ollama LLM scan extraction and use parser fallback only.",
    )
    parser.add_argument(
        "--ollama-model",
        default="llama3.1:8b",
        help="Ollama model name for scan extraction (default: llama3.1:8b).",
    )
    parser.add_argument(
        "--ollama-url",
        default="http://127.0.0.1:11434",
        help="Ollama base URL (default: http://127.0.0.1:11434).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    saved = run_pipeline(
        args.start_url,
        args.output,
        args.limit,
        use_scan_llm=not args.no_scan_llm,
        ollama_model=args.ollama_model,
        ollama_base_url=args.ollama_url,
    )
    print(f"Saved {saved} listings to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
