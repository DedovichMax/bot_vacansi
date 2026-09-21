# tests/test_main.py
import os
import tempfile
from unittest.mock import AsyncMock, Mock, patch

import pytest
import yaml

from main import check_and_notify, load_config


@pytest.fixture
def sample_config():
    """Sample config for testing."""
    return {
        "telegram": {
            "api_id": "12345",
            "api_hash": "test_hash",
            "bot_token": "test_token",
            "target_channel": "@test_channel",
        },
        "channels": ["@channel1", "@channel2"],
        "filters": [
            {"name": "Junior", "phrases": ["junior media buyer"], "exclude": [], "weight": 10}
        ],
        "schedule": {"check_interval_minutes": 15},
        "web": {"host": "0.0.0.0", "port": 8000},
        "logging": {"level": "INFO", "file": "logs/bot.log"},
    }


def test_load_config_reads_yaml():
    """Test that load_config reads YAML file correctly."""
    config_data = {"telegram": {"api_id": "123"}, "channels": ["@ch1"], "filters": []}

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_data, f)
        temp_path = f.name

    try:
        # Clear env overrides so load_dotenv doesn't overwrite test values
        with patch.dict(
            os.environ,
            {
                "TELEGRAM_API_ID": "",
                "TELEGRAM_API_HASH": "",
                "TELEGRAM_BOT_TOKEN": "",
                "TARGET_CHANNEL": "",
                "WEB_USERNAME": "",
                "WEB_PASSWORD": "",
            },
            clear=False,
        ):
            config = load_config(temp_path)
            assert config["telegram"]["api_id"] == "123"
            assert config["channels"] == ["@ch1"]
            assert config["filters"] == []
    finally:
        os.remove(temp_path)


def test_load_config_missing_file():
    """Test that load_config raises FileNotFoundError for missing file."""
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent_config.yaml")


def test_load_config_invalid_yaml():
    """Test that load_config raises for invalid YAML."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("{{invalid yaml: [")
        temp_path = f.name

    try:
        with pytest.raises(yaml.YAMLError):
            load_config(temp_path)
    finally:
        os.remove(temp_path)


@pytest.mark.asyncio
async def test_check_and_notify_filters_and_sends(sample_config):
    """Test that check_and_notify collects messages, filters, and sends notifications."""
    mock_collector = AsyncMock()
    mock_collector.check_channels.return_value = [
        {
            "channel": "channel1",
            "id": 100,
            "text": "Ищем junior media buyer без опыта",
            "link": "https://t.me/channel1/100",
        }
    ]

    mock_filter = Mock()
    mock_filter.check_message.return_value = [
        Mock(category="Junior", matched_phrase="junior media buyer", weight=10)
    ]

    mock_notifier = AsyncMock()
    mock_notifier.send_vacancy.return_value = True

    mock_db = Mock()

    await check_and_notify(mock_collector, mock_filter, mock_notifier, mock_db)

    mock_collector.check_channels.assert_called_once()
    mock_filter.check_message.assert_called_once_with("Ищем junior media buyer без опыта")
    mock_notifier.send_vacancy.assert_called_once()
    mock_db.add_vacancy.assert_called_once()


@pytest.mark.asyncio
async def test_check_and_notify_no_messages(sample_config):
    """Test that check_and_notify handles empty message list."""
    mock_collector = AsyncMock()
    mock_collector.check_channels.return_value = []

    mock_filter = Mock()
    mock_notifier = AsyncMock()
    mock_db = Mock()

    await check_and_notify(mock_collector, mock_filter, mock_notifier, mock_db)

    mock_collector.check_channels.assert_called_once()
    mock_filter.check_message.assert_not_called()
    mock_notifier.send_vacancy.assert_not_called()
    mock_db.add_vacancy.assert_not_called()


@pytest.mark.asyncio
async def test_check_and_notify_no_filter_matches(sample_config):
    """Test that check_and_notify skips messages with no filter matches."""
    mock_collector = AsyncMock()
    mock_collector.check_channels.return_value = [
        {
            "channel": "channel1",
            "id": 101,
            "text": "Продам квартиру",
            "link": "https://t.me/channel1/101",
        }
    ]

    mock_filter = Mock()
    mock_filter.check_message.return_value = []

    mock_notifier = AsyncMock()
    mock_db = Mock()

    await check_and_notify(mock_collector, mock_filter, mock_notifier, mock_db)

    mock_filter.check_message.assert_called_once_with("Продам квартиру")
    mock_notifier.send_vacancy.assert_not_called()
    mock_db.add_vacancy.assert_not_called()


@pytest.mark.asyncio
async def test_check_and_notify_sends_failure_logged(sample_config):
    """Test that check_and_notify logs error when notifier fails."""
    mock_collector = AsyncMock()
    mock_collector.check_channels.return_value = [
        {
            "channel": "channel1",
            "id": 102,
            "text": "junior media buyer",
            "link": "https://t.me/channel1/102",
        }
    ]

    mock_filter = Mock()
    mock_filter.check_message.return_value = [
        Mock(category="Junior", matched_phrase="junior media buyer", weight=10)
    ]

    mock_notifier = AsyncMock()
    mock_notifier.send_vacancy.return_value = False  # Send failed

    mock_db = Mock()

    await check_and_notify(mock_collector, mock_filter, mock_notifier, mock_db)

    mock_notifier.send_vacancy.assert_called_once()
    # vacancy should NOT be saved to DB since send failed
    mock_db.add_vacancy.assert_not_called()


@pytest.mark.asyncio
async def test_check_and_notify_collector_error(sample_config):
    """Test that check_and_notify handles collector errors gracefully."""
    mock_collector = AsyncMock()
    mock_collector.check_channels.side_effect = Exception("Connection failed")

    mock_filter = Mock()
    mock_notifier = AsyncMock()
    mock_notifier.send_error.return_value = True

    mock_db = Mock()

    await check_and_notify(mock_collector, mock_filter, mock_notifier, mock_db)

    mock_db.log_error.assert_called_once()
    mock_notifier.send_error.assert_called_once()


@pytest.mark.asyncio
async def test_check_and_notify_multiple_matches(sample_config):
    """Test that check_and_notify handles multiple filter matches per message."""
    mock_collector = AsyncMock()
    mock_collector.check_channels.return_value = [
        {
            "channel": "channel1",
            "id": 200,
            "text": "junior media buyer без опыта",
            "link": "https://t.me/channel1/200",
        }
    ]

    mock_filter = Mock()
    mock_filter.check_message.return_value = [
        Mock(category="Junior", matched_phrase="junior media buyer", weight=10),
        Mock(category="Без опыта", matched_phrase="без опыта", weight=8),
    ]

    mock_notifier = AsyncMock()
    mock_notifier.send_vacancy.return_value = True

    mock_db = Mock()

    await check_and_notify(mock_collector, mock_filter, mock_notifier, mock_db)

    # Should send 2 notifications
    assert mock_notifier.send_vacancy.call_count == 2
    # Should save 2 vacancies
    assert mock_db.add_vacancy.call_count == 2


def test_load_config_preserves_all_sections(sample_config):
    """Test that load_config preserves all config sections."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(sample_config, f)
        temp_path = f.name

    try:
        config = load_config(temp_path)
        assert "telegram" in config
        assert "channels" in config
        assert "filters" in config
        assert "schedule" in config
        assert "web" in config
        assert "logging" in config
    finally:
        os.remove(temp_path)
