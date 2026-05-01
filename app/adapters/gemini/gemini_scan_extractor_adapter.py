from __future__ import annotations

import json
import re
from typing import Any, Dict

import requests

from app.core.ports.scan_extractor_port import ScanExtractorPort


class GeminiScanExtractorAdapter(ScanExtractorPort):
    def __init__(
        self,
        api_key: str,
        model: str = "gemini-3.1-flash-lite-preview",
        timeout: int = 45,
    ) -> None:
        self.api_key = api_key.strip()
        self.model = model
        self.timeout = timeout

    def analyze_description(self, description: str) -> Dict[str, Any]:
        if not self.api_key or not description.strip():
            return {}

        payload: Dict[str, Any] = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": _build_prompt(description)}],
                }
            ],
            "generationConfig": {
                "temperature": 0,
                "responseMimeType": "application/json",
            },
        }
        last_error: Exception | None = None
        for model_name in _candidate_models(self.model):
            try:
                response = requests.post(
                    _build_url(self.api_key, model_name),
                    json=payload,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                data = response.json()
                raw = _extract_text(data)
                return _normalize_output(raw)
            except requests.HTTPError as exc:
                last_error = exc
                status_code = getattr(exc.response, "status_code", None)
                if status_code in {400, 404}:
                    continue
                raise
        if last_error:
            raise last_error
        return {}


def _build_url(api_key: str, model: str) -> str:
    return (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )


def _candidate_models(model: str) -> list[str]:
    candidates = [
        model,
        "gemini-3.1-flash-lite-preview",
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash-002",
    ]
    unique: list[str] = []
    for candidate in candidates:
        candidate = candidate.strip()
        if candidate and candidate not in unique:
            unique.append(candidate)
    return unique


def _build_prompt(description: str) -> str:
    return (
        "You are extracting car inspection details from Arabic car text.\n"
        "Return a single JSON object only, with these keys and types (no extra keys):\n"
        "- chassis_score: integer between 0 and 7 (0 = worst, 7 = best)\n"
        "- front_left: short label/string (e.g. Good, Very Good, Bad, Repaired, Painted, Damaged)\n"
        "- front_right: short label/string\n"
        "- rear_left: short label/string\n"
        "- rear_right: short label/string\n"
        "- used_in_apps: boolean (true or false)\n"
        "Only output valid JSON matching that schema. Do NOT repeat this instruction or include any explanatory text.\n"
        f"Description: {description}\n"
        "Output:"
    )


def _extract_text(data: Dict[str, Any]) -> str:
    candidates = data.get("candidates", [])
    if not isinstance(candidates, list) or not candidates:
        return ""
    candidate = candidates[0]
    if not isinstance(candidate, dict):
        return ""
    content = candidate.get("content", {})
    if not isinstance(content, dict):
        return ""
    parts = content.get("parts", [])
    if not isinstance(parts, list):
        return ""
    texts = [str(part.get("text", "")) for part in parts if isinstance(part, dict) and part.get("text")]
    return "".join(texts).strip()


def _normalize_output(value: str) -> Dict[str, Any]:
    text = _strip_code_fences(value.strip().strip('"').strip("'"))
    if not text:
        return {}

    if text.startswith("{") and text.endswith("}"):
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = {}
    else:
        parsed = {"scan": text}

    if not isinstance(parsed, dict):
        return {}

    chassis_score = _normalize_chassis_score(parsed.get("chassis_score", ""))
    front_left = _normalize_corner_label(parsed.get("front_left", ""))
    front_right = _normalize_corner_label(parsed.get("front_right", ""))
    rear_left = _normalize_corner_label(parsed.get("rear_left", ""))
    rear_right = _normalize_corner_label(parsed.get("rear_right", ""))
    used_in_apps = _normalize_bool(parsed.get("used_in_apps", ""))

    result: Dict[str, Any] = {}
    if chassis_score is not None:
        result["chassis_score"] = chassis_score
    if front_left:
        result["front_left"] = front_left
    if front_right:
        result["front_right"] = front_right
    if rear_left:
        result["rear_left"] = rear_left
    if rear_right:
        result["rear_right"] = rear_right
    if used_in_apps is not None:
        result["used_in_apps"] = used_in_apps
    return result


def _strip_code_fences(value: str) -> str:
    fenced = re.match(r"^```(?:json)?\s*(.*?)\s*```$", value, re.DOTALL | re.IGNORECASE)
    if fenced:
        return fenced.group(1).strip()
    return value


def _clean_text(value: Any, keep_accident_tokens: bool = False) -> str:
    text = str(value).strip().strip('"').strip("'")
    text = " ".join(text.split())
    if not keep_accident_tokens:
        text = text.replace("الفحص", "").replace("فحص", "").strip(" :-")
    return text


def _normalize_chassis_score(value: Any) -> int | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    try:
        number = int(float(str(value).strip()))
    except ValueError:
        return None
    if number < 0:
        return 0
    if number > 7:
        return 7
    return number


def _normalize_corner_label(value: Any) -> str:
    text = _clean_text(value, keep_accident_tokens=True)
    if not text:
        return ""
    lowered = text.lower()
    mapping = {
        "good": "Good",
        "very good": "Very Good",
        "vg": "Very Good",
        "bad": "Bad",
        "damaged": "Damaged",
        "repaired": "Repaired",
        "painted": "Painted",
        "excellent": "Excellent",
        "fair": "Fair",
        "clean": "Good",
        "جيد": "Good",
        "جيد جدا": "Very Good",
        "ممتاز": "Excellent",
        "سيئ": "Bad",
        "مضرور": "Damaged",
        "مصلح": "Repaired",
        "مرشوش": "Painted",
    }
    if lowered in mapping:
        return mapping[lowered]
    return text[:40]


def _normalize_bool(value: Any) -> bool | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    text = _clean_text(value, keep_accident_tokens=True).lower()
    if text in {"true", "1", "yes", "y", "نعم"}:
        return True
    if text in {"false", "0", "no", "n", "لا"}:
        return False
    return None
