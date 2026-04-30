from __future__ import annotations

import base64
import os
import sys
from typing import Any, Dict

import requests

from app.core.ports.car_fetcher_port import CarFetcherPort

ZYTE_API_URL = "https://api.zyte.com/v1/extract"


class ZyteFetcherAdapter(CarFetcherPort):
    def __init__(
        self,
        api_key: str | None = None,
        timeout: int = 60,
        browser_html: bool = True,
        follow_redirect: bool = False,
    ) -> None:
        _load_env_file(".env")
        self.api_key = api_key or os.getenv("ZYTE_API_KEY", "")
        self.timeout = timeout
        self.browser_html = browser_html
        self.follow_redirect = follow_redirect

    def fetch_listing_page_html(self, url: str) -> str:
        return self._fetch_html(url)

    def fetch_listing_detail_html(self, url: str) -> str:
        return self._fetch_html(url)

    def _fetch_html(self, url: str) -> str:
        if not self.api_key:
            raise RuntimeError("Missing ZYTE_API_KEY environment variable.")

        payload = _build_payload(
            url,
            browser_html=self.browser_html,
            http_response_body=not self.browser_html,
            follow_redirect=self.follow_redirect,
        )
        response = requests.post(
            ZYTE_API_URL,
            auth=(self.api_key, ""),
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()

        if self.browser_html:
            body = data.get("browserHtml")
            if not body:
                raise RuntimeError("No browserHtml in response.")
            return body

        encoded = data.get("httpResponseBody")
        if not encoded:
            raise RuntimeError("No httpResponseBody in response.")
        return base64.b64decode(encoded).decode("utf-8", errors="ignore")


def _build_payload(
    url: str,
    browser_html: bool,
    http_response_body: bool,
    follow_redirect: bool,
) -> Dict[str, Any]:
    return {
        "url": url,
        "browserHtml": browser_html,
        "httpResponseBody": http_response_body,
        "followRedirect": follow_redirect,
    }


def _load_env_file(path: str) -> None:
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
    except OSError as exc:
        print(f"Failed to read .env file: {exc}", file=sys.stderr)
