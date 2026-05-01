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

SCAN_KEY = "Scan"
DESCRIPTION_KEY = "Description"
SCAN_TOKENS = {"\u0641\u062d\u0635", "\u0627\u0644\u0641\u062d\u0635"}


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


def extract_scan(description: str) -> str:
    if not description:
        return ""
    text = clean_text(description)
    if not text:
        return ""
    text = re.sub(r"[\.:;,\-\u060c\u061b]", " ", text)
    text = re.sub(r"(\d)(\D)", r"\1 \2", text)
    text = re.sub(r"(\D)(\d)", r"\1 \2", text)
    tokens = [token for token in text.split() if token]
    for index, token in enumerate(tokens):
        if token in SCAN_TOKENS:
            after = tokens[index + 1 : index + 4]
            if not after:
                return ""
            if not any(_contains_digit(value) for value in after):
                extended = tokens[index + 1 : index + 7]
                if any(_contains_digit(value) for value in extended):
                    after = extended[:3]
                else:
                    return ""
            return " ".join(after)
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
    scan_value = extract_scan(description)
    if scan_value:
        data[SCAN_KEY] = scan_value

    return data


def _contains_digit(value: str) -> bool:
    return any(char.isdigit() for char in value)
