from __future__ import annotations

import json
from typing import Any, Dict

import requests

from app.core.ports.scan_extractor_port import ScanExtractorPort


class OllamaScanExtractorAdapter(ScanExtractorPort):
    def __init__(
        self,
        model: str = "llama3.1:8b",
        base_url: str = "http://127.0.0.1:11434",
        timeout: int = 45,
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def extract_scan(self, description: str) -> str:
        if not description.strip():
            return ""

        prompt = _build_prompt(description)
        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0},
        }
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()
        raw = str(data.get("response", "")).strip()
        return _normalize_output(raw)


def _build_prompt(description: str) -> str:
    return (
        "You are an information extractor.\\n"
        "Task: extract ONLY the inspection fragment (فحص) from this Arabic car description.\\n"
        "Rules:\\n"
        "1) Return plain text only, no explanation.\\n"
        "2) Return empty string if no فحص/alفحص token exists.\\n"
        "3) Result should be short, usually up to 3 words after فحص and must include a number when available.\\n"
        "4) Do not include the word فحص itself in the output.\\n"
        f"Description: {description}\\n"
        "Output:"
    )


def _normalize_output(value: str) -> str:
    text = value.strip().strip('"').strip("'")
    if not text:
        return ""

    # Accept JSON-like responses if model returns structured text.
    if text.startswith("{") and text.endswith("}"):
        try:
            obj = json.loads(text)
            candidate = obj.get("scan", "") if isinstance(obj, dict) else ""
            text = str(candidate).strip()
        except json.JSONDecodeError:
            pass

    lowered = text.replace("الفحص", "").replace("فحص", "").strip(" :-")
    return " ".join(lowered.split())
