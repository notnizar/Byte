from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from app.core.services.scraper_service import ScraperService


class ScraperServiceTests(unittest.TestCase):
    @patch("app.core.services.scraper_service.extract_fields")
    @patch("app.core.services.scraper_service.parse_listings")
    @patch("app.core.services.scraper_service.get_base_url")
    def test_runs_gemini_only_for_used_listings(self, get_base_url: Mock, parse_listings: Mock, extract_fields: Mock) -> None:
        fetcher = Mock()
        fetcher.fetch_listing_page_html.return_value = "<html></html>"
        fetcher.fetch_listing_detail_html.side_effect = ["detail-used", "detail-new"]

        repository = Mock()
        url_resolver = Mock()
        url_resolver.resolve_detail_url.side_effect = ["https://example.com/used", "https://example.com/new"]

        analyzer = Mock()
        analyzer.analyze_description.return_value = {
            "chassis_score": 7,
            "front_left": "Good",
            "front_right": "Good",
            "rear_left": "Good",
            "rear_right": "Damaged",
            "used_in_apps": False,
        }

        get_base_url.return_value = "https://example.com"
        parse_listings.return_value = [
            {"id": "1", "price": "1000", "url": "https://example.com/used"},
            {"id": "2", "price": "2000", "url": "https://example.com/new"},
        ]
        extract_fields.side_effect = [
            {"Condition": "Used", "Description": "فحص 7 جيد", "price": "1000"},
            {"Condition": "New", "Description": "فحص 5 جيد", "price": "2000"},
        ]

        service = ScraperService(fetcher, repository, url_resolver, scan_extractor=analyzer)
        saved = service.run("https://example.com/toyota", limit=2)

        self.assertEqual(saved, 2)
        analyzer.analyze_description.assert_called_once_with("فحص 7 جيد")
        self.assertEqual(repository.save.call_count, 2)

        first_saved = repository.save.call_args_list[0].args[0].to_dict()
        second_saved = repository.save.call_args_list[1].args[0].to_dict()
        self.assertEqual(first_saved["url"], "https://example.com/used")
        self.assertEqual(second_saved["url"], "https://example.com/new")
        self.assertEqual(first_saved["chassis_score"], 7)
        self.assertEqual(first_saved["front_left"], "Good")
        self.assertEqual(first_saved["front_right"], "Good")
        self.assertEqual(first_saved["rear_left"], "Good")
        self.assertEqual(first_saved["rear_right"], "Damaged")
        self.assertEqual(first_saved["used_in_apps"], False)
        self.assertNotIn("chassis_score", second_saved)


if __name__ == "__main__":
    unittest.main()