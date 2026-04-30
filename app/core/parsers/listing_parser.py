from __future__ import annotations

import re
from html import unescape
from typing import Dict

FIELDS = [
    "Condition",
    "Model",
    "Car Make",
    "Transmission",
    "Car License",
    "City",
    "Published Date",
]


def strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def clean_text(text: str) -> str:
    return unescape(strip_tags(text)).strip()


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


def extract_fields(html: str) -> Dict[str, str]:
    pairs = extract_pairs(html)
    data = {field: pairs.get(field, "") for field in FIELDS}

    if not data["Published Date"]:
        data["Published Date"] = extract_json_label(html, "Published Date")
    if not data["Car License"]:
        data["Car License"] = extract_json_label(html, "Car License")

    return data
