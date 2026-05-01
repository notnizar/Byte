from __future__ import annotations

import json
import re
from typing import Dict

from app.core.parsers.common import clean_text

FIELDS = [
    "price",
    "Condition",
    "Car Make",
    "Model",
    "Year",
    "Fuel",
    "Exterior Color",
    "Interior Color",
    "Neighborhood",
    "City",
    "Kilometers",
    "Published Date",
]

DESCRIPTION_KEY = "Description"


def extract_pairs(html: str) -> Dict[str, str]:
    pairs: Dict[str, str] = {}
    for label, value in re.findall(r"<span[^>]*>([^<]+)</span>\s*<a[^>]*>([^<]+)</a>", html):
        label_clean = clean_text(label)
        value_clean = clean_text(value)
        if label_clean and value_clean and label_clean not in pairs:
            pairs[label_clean] = value_clean
    return pairs


def extract_json_label(html: str, label: str) -> str:
    patterns = [
        rf'"label"\s*:\s*"{re.escape(label)}"\s*,\s*"value"\s*:\s*"([^"]*)"',
        rf"{re.escape(label)}\\\",\\\"value\\\":\\\"([^\\\"]*)",
        rf'{re.escape(label)}","value":"([^"]*)',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ""


def extract_price(html: str) -> str:
    patterns = [
        r'class="price"[^>]*>\s*([^<]+)',
        r'class="redColor bold font-18"[^>]*>\s*([^<]+)',
        r'"price"\s*:\s*"([^"]+)"',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return clean_text(match.group(1))
    return ""


def extract_description(html: str) -> str:
    patterns = [
        r'"description"\s*:\s*"([^"]+)"',
        r'"postDescription"\s*:\s*"([^"]+)"',
        r'<meta[^>]+name="description"[^>]+content="([^"]+)"',
        r'itemprop="description"[^>]*>(.*?)</',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
        if not match:
            continue
        value = match.group(1).strip()
        if not value:
            continue
        if "\\" in value:
            try:
                value = json.loads(f'"{value}"')
            except json.JSONDecodeError:
                value = value.replace("\\n", " ")
        return clean_text(value)
    return ""


def extract_fields(html: str) -> Dict[str, str]:
    pairs = extract_pairs(html)
    data = {field: pairs.get(field, "") for field in FIELDS}

    if not data["price"]:
        data["price"] = extract_price(html)

    for field in FIELDS:
        if field == "price":
            continue
        if not data[field]:
            data[field] = extract_json_label(html, field)

    description = extract_description(html)
    if description:
        data[DESCRIPTION_KEY] = description

    return data
