from __future__ import annotations

import re
from html import unescape
from typing import Dict, List


def strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def clean_text(text: str) -> str:
    return unescape(strip_tags(text)).strip()


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
        title_match = re.search(r"<h2[^>]*>(.*?)</h2>", item, re.DOTALL)
        price_match = re.search(r'<div class="redColor bold font-18">(.*?)</div>', item, re.DOTALL)
        location_match = re.search(
            r'<div class="flex alignItems font-13 bold">.*?<span[^>]*>(.*?)</span>',
            item,
            re.DOTALL,
        )

        listing_id = str(index)

        url = ""
        if href_match:
            href = href_match.group(1)
            url = href if href.startswith("http") else f"{base_url_clean}{href}" if base_url_clean else href

        title = clean_text(title_match.group(1)) if title_match else ""
        location = clean_text(location_match.group(1)) if location_match else ""

        price_info = {"price": "", "currency": "", "price_raw": ""}
        if price_match:
            price_info = parse_price(price_match.group(1))

        listings.append(
            {
                "id": listing_id,
                "title": title,
                "price": price_info["price"],
                "currency": price_info["currency"],
                "location": location,
                "url": url,
            }
        )

    return listings
