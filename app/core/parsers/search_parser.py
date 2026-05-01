from __future__ import annotations

import re
from typing import Dict, List

from app.core.parsers.common import clean_text


def parse_price(price_text: str) -> Dict[str, str]:
    cleaned = clean_text(price_text)
    parts = cleaned.split()
    currency = parts[-1] if parts else ""
    amount = cleaned.replace(currency, "").strip()
    amount = re.sub(r"[^0-9.,]", "", amount).replace(",", "")
    return {"price": amount, "currency": currency, "price_raw": cleaned}


def parse_listings(html: str, base_url: str) -> List[Dict[str, str]]:
    listings = []
    base_url_clean = base_url.rstrip("/") if base_url else ""
    pattern = re.compile(r'<a href="/en/search/\d+"[^>]*>.*?</a>', re.DOTALL)
    for index, match in enumerate(pattern.finditer(html), start=1):
        item = match.group(0)
        href_match = re.search(r'href="([^"]+)"', item)
        price_match = re.search(r'<div class="redColor bold font-18">(.*?)</div>', item, re.DOTALL)

        listing_id = str(index)

        url = ""
        if href_match:
            href = href_match.group(1)
            url = href if href.startswith("http") else f"{base_url_clean}{href}" if base_url_clean else href

        price_info = {"price": "", "currency": "", "price_raw": ""}
        if price_match:
            price_info = parse_price(price_match.group(1))

        listings.append(
            {
                "id": listing_id,
                "price": price_info["price"],
                "currency": price_info["currency"],
                "url": url,
            }
        )

    return listings
