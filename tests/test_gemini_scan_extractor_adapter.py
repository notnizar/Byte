from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

import requests

from app.adapters.gemini.gemini_scan_extractor_adapter import GeminiScanExtractorAdapter, _build_prompt, _normalize_output


class GeminiScanExtractorAdapterTests(unittest.TestCase):
    def test_build_prompt_requests_json_only(self) -> None:
        prompt = _build_prompt("فحص 7 جيد")
        self.assertIn('JSON object only', prompt)
        self.assertIn('chassis_score', prompt)
        self.assertIn('used_in_apps', prompt)

    def test_normalize_output_parses_json_response(self) -> None:
        raw = '{"chassis_score": 7, "front_left": "Good", "front_right": "Good", "rear_left": "Good", "rear_right": "Good", "used_in_apps": false}'
        self.assertEqual(
            _normalize_output(raw),
            {
                "chassis_score": 7,
                "front_left": "Good",
                "front_right": "Good",
                "rear_left": "Good",
                "rear_right": "Good",
                "used_in_apps": False,
            },
        )

    def test_normalize_output_strips_code_fences(self) -> None:
        raw = "```json\n{\"chassis_score\": \"6\", \"front_left\": \"جيد\", \"front_right\": \"جيد جدا\", \"rear_left\": \"مصلح\", \"rear_right\": \"مرشوش\", \"used_in_apps\": \"true\"}\n```"
        self.assertEqual(
            _normalize_output(raw),
            {
                "chassis_score": 6,
                "front_left": "Good",
                "front_right": "Very Good",
                "rear_left": "Repaired",
                "rear_right": "Painted",
                "used_in_apps": True,
            },
        )

    @patch("app.adapters.gemini.gemini_scan_extractor_adapter.requests.post")
    def test_analyze_description_uses_gemini_response(self, post: Mock) -> None:
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": '{"chassis_score": 4, "front_left": "Good", "front_right": "Good", "rear_left": "Good", "rear_right": "Damaged", "used_in_apps": false}'
                            }
                        ]
                    }
                }
            ]
        }
        post.return_value = response

        adapter = GeminiScanExtractorAdapter(api_key="test-key")
        result = adapter.analyze_description("فحص 4 جيد")

        self.assertEqual(
            result,
            {
                "chassis_score": 4,
                "front_left": "Good",
                "front_right": "Good",
                "rear_left": "Good",
                "rear_right": "Damaged",
                "used_in_apps": False,
            },
        )
        post.assert_called_once()

    @patch("app.adapters.gemini.gemini_scan_extractor_adapter.requests.post")
    def test_empty_api_key_returns_empty_result(self, post: Mock) -> None:
        adapter = GeminiScanExtractorAdapter(api_key="")
        result = adapter.analyze_description("فحص 4 جيد")

        self.assertEqual(result, {})
        post.assert_not_called()

    @patch("app.adapters.gemini.gemini_scan_extractor_adapter.requests.post")
    def test_analyze_description_falls_back_from_bad_model_name(self, post: Mock) -> None:
        bad_response = Mock()
        bad_response.status_code = 404
        bad_error = requests.HTTPError("404 Client Error: Not Found")
        bad_error.response = bad_response
        bad_response.raise_for_status.side_effect = bad_error

        good_response = Mock()
        good_response.raise_for_status.return_value = None
        good_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": '{"chassis_score": 7, "front_left": "Good", "front_right": "Good", "rear_left": "Good", "rear_right": "Good", "used_in_apps": false}'
                            }
                        ]
                    }
                }
            ]
        }
        post.side_effect = [bad_response, good_response]

        adapter = GeminiScanExtractorAdapter(api_key="test-key", model="gemini-1.5-flash")
        result = adapter.analyze_description("فحص 7 جيد")

        self.assertEqual(result["chassis_score"], 7)
        self.assertEqual(post.call_count, 2)


if __name__ == "__main__":
    unittest.main()
