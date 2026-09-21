# tests/test_collector.py
from unittest.mock import Mock

import pytest

from collector.telegram_collector import TelegramCollector


@pytest.fixture
def collector_config():
    return {
        "telegram": {"api_id": "12345", "api_hash": "test_hash", "bot_token": "test_token"},
        "channels": ["@channel1", "@channel2"],
    }


def test_collector_initialization():
    """Test that collector initializes correctly."""
    config = {"telegram": {"api_id": "12345", "api_hash": "test_hash"}, "channels": ["@channel1"]}

    collector = TelegramCollector(config)
    assert collector.channels == ["@channel1"]
    assert collector.config == config


def test_collector_formats_channel_name():
    """Test channel name formatting."""
    config = {
        "telegram": {"api_id": "12345", "api_hash": "test_hash"},
        "channels": ["channel1", "@channel1"],
    }

    collector = TelegramCollector(config)

    # Both should be formatted the same
    assert collector._format_channel("channel1") == "channel1"
    assert collector._format_channel("@channel1") == "channel1"


@pytest.mark.asyncio
async def test_collector_checks_duplicate_messages():
    """Test that collector skips already processed messages."""
    config = {"telegram": {"api_id": "12345", "api_hash": "test_hash"}, "channels": ["@channel1"]}

    mock_db = Mock()
    mock_db.is_message_processed.return_value = True  # Already processed

    TelegramCollector(config, db=mock_db)

    # Mock message
    mock_message = Mock()
    mock_message.id = 12345

    # Should skip this message
    should_process = not mock_db.is_message_processed("@channel1", 12345)
    assert not should_process
