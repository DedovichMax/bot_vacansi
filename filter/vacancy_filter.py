# filter/vacancy_filter.py
from dataclasses import dataclass
from typing import Any


@dataclass
class FilterResult:
    """Result of filter matching."""

    category: str
    matched_phrase: str
    weight: int
    original_text: str


class VacancyFilter:
    def __init__(self, config: dict[str, Any]):
        """Initialize filter with config."""
        self.filters = config.get("filters", [])

    def check_message(self, message_text: str) -> list[FilterResult]:
        """Check message against all filters."""
        results = []

        for filter_config in self.filters:
            category = filter_config["name"]
            phrases = filter_config.get("phrases", [])
            exclude = filter_config.get("exclude", [])
            weight = filter_config.get("weight", 5)

            # Check if any exclude word is present
            if self._has_exclude_word(message_text, exclude):
                continue

            # Check for phrase matches
            matched_phrase = self._find_phrase_match(message_text, phrases)
            if matched_phrase:
                results.append(
                    FilterResult(
                        category=category,
                        matched_phrase=matched_phrase,
                        weight=weight,
                        original_text=message_text,
                    )
                )

        return results

    def _has_exclude_word(self, text: str, exclude_words: list[str]) -> bool:
        """Check if text contains any exclude word."""
        text_lower = text.lower()
        for word in exclude_words:
            if word.lower() in text_lower:
                return True
        return False

    def _find_phrase_match(self, text: str, phrases: list[str]) -> str | None:
        """Find exact phrase match in text."""
        text_lower = text.lower()
        for phrase in phrases:
            if phrase.lower() in text_lower:
                return phrase
        return None
