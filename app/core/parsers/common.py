from __future__ import annotations

import re
from html import unescape


def strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def clean_text(text: str) -> str:
    return unescape(strip_tags(text)).strip()
