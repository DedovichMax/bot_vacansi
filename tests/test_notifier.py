# tests/test_notifier.py

import pytest

from filter.vacancy_filter import FilterResult
from notifier.telegram_notifier import TelegramNotifier


@pytest.fixture
def notifier_config():
    return {"telegram": {"bot_token": "test_token", "target_channel": "@test_channel"}}


def test_notifier_initialization():
    """Test that notifier initializes correctly."""
    config = {"telegram": {"bot_token": "test_token", "target_channel": "@test_channel"}}

    notifier = TelegramNotifier(config)
    assert notifier.target_channel == "test_channel"


def test_notifier_formats_message():
    """Test message formatting."""
    config = {"telegram": {"bot_token": "test_token", "target_channel": "@test_channel"}}

    notifier = TelegramNotifier(config)

    vacancy = FilterResult(
        category="Junior позиции",
        matched_phrase="junior media buyer",
        weight=10,
        original_text="Ищем junior media buyer без опыта",
    )

    message = notifier.format_message(vacancy)

    assert "Junior позиции" in message
    assert "junior media buyer" in message
    assert "Ищем junior media buyer без опыта" in message


def test_notifier_strips_channel_prefix():
    """Test that channel prefix is stripped."""
    config = {"telegram": {"bot_token": "test_token", "target_channel": "@test_channel"}}

    notifier = TelegramNotifier(config)
    assert notifier.target_channel == "test_channel"
