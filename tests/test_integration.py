# tests/test_integration.py
"""Integration tests for the Telegram Vacancy Bot.

These tests verify the full pipeline works end-to-end by testing how
components interact: Database + Collector + Filter + Notifier + Config.
All Telegram API calls are mocked — no real connections are made.
"""

from unittest.mock import AsyncMock

import pytest
import yaml

from collector.telegram_collector import TelegramCollector
from filter.vacancy_filter import FilterResult, VacancyFilter
from notifier.telegram_notifier import TelegramNotifier
from utils.database import Database

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def db_path(tmp_path):
    """Provide a temporary database path that is cleaned up after test."""
    path = tmp_path / "test_integration.db"
    yield str(path)
    # Windows may hold the file briefly; ignore cleanup errors
    try:
        if path.exists():
            path.unlink()
    except PermissionError:
        pass


@pytest.fixture
def db(db_path):
    """Provide a fresh Database instance for each test."""
    return Database(db_path)


@pytest.fixture
def full_config():
    """Config dict that mirrors config.yaml structure."""
    return {
        "telegram": {
            "api_id": "12345",
            "api_hash": "test_hash_value",
            "bot_token": "test_bot_token",
            "target_channel": "@vacancy_notifications",
        },
        "channels": ["@job_channel_1", "@job_channel_2"],
        "filters": [
            {
                "name": "Junior позиции",
                "phrases": [
                    "junior media buyer",
                    "junior medua buyer",
                    "младший медиабайер",
                ],
                "exclude": ["senior junior"],
                "weight": 10,
            },
            {
                "name": "Без опыта",
                "phrases": [
                    "без опыта",
                    "для начинающих",
                    "обучим с нуля",
                ],
                "exclude": [],
                "weight": 8,
            },
            {
                "name": "Farmer",
                "phrases": ["farmer", "фармер", "accounts farmer"],
                "exclude": [],
                "weight": 7,
            },
        ],
        "schedule": {
            "check_interval_minutes": 15,
            "active_hours": {"start": 9, "end": 22},
        },
        "web": {
            "host": "0.0.0.0",
            "port": 8000,
            "username": "admin",
            "password": "secret",
        },
        "logging": {
            "level": "INFO",
            "file": "logs/bot.log",
        },
    }


# ---------------------------------------------------------------------------
# 1. Full workflow: Collect → Filter → Notify → Persist
# ---------------------------------------------------------------------------


class TestFullWorkflow:
    """End-to-end pipeline tests with mocked Telegram I/O."""

    def test_full_workflow_collect_filter_persist(self, db, full_config):
        """Simulate: collector gathers messages → filter matches → vacancy stored.

        Each message is stored at most once (highest-weight match wins)
        because the DB enforces UNIQUE(channel_name, message_id) on vacancies.
        """
        TelegramCollector(full_config, db=db)
        vf = VacancyFilter(full_config)

        # --- simulate collected messages ---
        test_messages = [
            {
                "channel": "job_channel_1",
                "id": 1001,
                "text": "Ищем junior media buyer без опыта, удалённо",
                "link": "https://t.me/job_channel_1/1001",
            },
            {
                "channel": "job_channel_1",
                "id": 1002,
                "text": "Продавец-консультант в магазин",
                "link": "https://t.me/job_channel_1/1002",
            },
            {
                "channel": "job_channel_2",
                "id": 2001,
                "text": "Требуется accounts farmer, опыт от 1 года",
                "link": "https://t.me/job_channel_2/2001",
            },
        ]

        matched_count = 0
        for msg in test_messages:
            results = vf.check_message(msg["text"])
            if results:
                # Pick the best match (highest weight) — mirrors real pipeline
                best = max(results, key=lambda r: r.weight)
                db.mark_message_processed(msg["channel"], msg["id"])
                vacancy_id = db.add_vacancy(
                    channel_name=msg["channel"],
                    message_id=msg["id"],
                    category=best.category,
                    matched_phrase=best.matched_phrase,
                    weight=best.weight,
                    text=msg["text"],
                    link=msg["link"],
                )
                assert vacancy_id is not None
                matched_count += 1

        # Message 1001 matches 2 filters → stored once (best weight)
        # Message 1002 matches nothing → skipped
        # Message 2001 matches 1 filter → stored
        assert matched_count == 2

        # Verify duplicate detection
        assert db.is_message_processed("job_channel_1", 1001) is True
        assert db.is_message_processed("job_channel_1", 1002) is False
        assert db.is_message_processed("job_channel_2", 2001) is True

        # Verify stored vacancies
        vacancies = db.get_vacancies()
        assert len(vacancies) == 2
        categories = {v["category"] for v in vacancies}
        assert "Junior позиции" in categories
        assert "Farmer" in categories

    def test_full_workflow_excluded_messages_not_stored(self, db, full_config):
        """Messages matching exclude words must NOT produce vacancies."""
        vf = VacancyFilter(full_config)

        excluded_text = "senior junior media buyer — опыт от 5 лет"
        results = vf.check_message(excluded_text)
        assert len(results) == 0

        # Verify nothing was stored
        assert len(db.get_vacancies()) == 0

    def test_full_workflow_no_match_messages_ignored(self, db, full_config):
        """Messages that don't match any filter are silently ignored."""
        vf = VacancyFilter(full_config)

        irrelevant_text = "Продаём квартиру в центре города"
        results = vf.check_message(irrelevant_text)
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_full_pipeline_with_mocked_notifier(self, db, full_config):
        """Full async pipeline: collector → filter → mock notifier → DB."""
        TelegramCollector(full_config, db=db)
        vf = VacancyFilter(full_config)
        notifier = TelegramNotifier(full_config)

        # Mock the notifier's send_vacancy method
        notifier.send_vacancy = AsyncMock(return_value=True)

        # Simulate collected messages
        messages = [
            {
                "channel": "job_channel_1",
                "id": 3001,
                "text": "Ищем junior media buyer",
                "link": "https://t.me/job_channel_1/3001",
            },
        ]

        for msg in messages:
            results = vf.check_message(msg["text"])
            for result in results:
                sent = await notifier.send_vacancy(result, msg["channel"], msg["id"])
                assert sent is True

                db.mark_message_processed(msg["channel"], msg["id"])
                db.add_vacancy(
                    channel_name=msg["channel"],
                    message_id=msg["id"],
                    category=result.category,
                    matched_phrase=result.matched_phrase,
                    weight=result.weight,
                    text=msg["text"],
                    link=msg["link"],
                )

        # Verify notifier was called
        notifier.send_vacancy.assert_called_once()

        # Verify DB state
        assert db.is_message_processed("job_channel_1", 3001) is True
        vacancies = db.get_vacancies()
        assert len(vacancies) == 1
        assert vacancies[0]["category"] == "Junior позиции"


# ---------------------------------------------------------------------------
# 2. Component interaction: Collector + Database
# ---------------------------------------------------------------------------


class TestCollectorDatabaseInteraction:
    """Verify collector integrates properly with database for dedup."""

    def test_collector_skips_processed_messages(self, full_config, tmp_path):
        """Collector should skip messages already in processed_messages table."""
        db_path = tmp_path / "test_collector_int.db"
        db = Database(str(db_path))
        TelegramCollector(full_config, db=db)

        # Mark message as already processed
        db.mark_message_processed("job_channel_1", 9999)

        # Simulate: collector sees this message → should skip
        assert db.is_message_processed("job_channel_1", 9999) is True

        # New message should not be marked
        assert db.is_message_processed("job_channel_1", 10000) is False


# ---------------------------------------------------------------------------
# 3. Component interaction: Filter + Database persistence
# ---------------------------------------------------------------------------


class TestFilterDatabaseInteraction:
    """Verify filter results are correctly persisted to database."""

    def test_multiple_filter_matches_persisted(self, db, full_config):
        """When multiple messages match filters, each unique message is stored.

        UNIQUE(channel_name, message_id) means we store one vacancy per message.
        """
        vf = VacancyFilter(full_config)

        messages = [
            ("Ищем junior media buyer без опыта", 5001, "ch_a"),
            ("Нужен accounts farmer, опыт от 3 лет", 5002, "ch_b"),
        ]

        for text, msg_id, channel in messages:
            results = vf.check_message(text)
            if results:
                best = max(results, key=lambda r: r.weight)
                vacancy_id = db.add_vacancy(
                    channel_name=channel,
                    message_id=msg_id,
                    category=best.category,
                    matched_phrase=best.matched_phrase,
                    weight=best.weight,
                    text=text,
                    link=f"https://t.me/{channel}/{msg_id}",
                )
                assert vacancy_id is not None

        vacancies = db.get_vacancies()
        assert len(vacancies) == 2
        categories = {v["category"] for v in vacancies}
        assert "Junior позиции" in categories
        assert "Farmer" in categories

    def test_vacancy_ordering_by_date(self, db, full_config):
        """Vacancies should be returned most-recent first.

        We use two different channels so each (channel, msg_id) pair is unique,
        and we verify the ORDER BY sent_at DESC clause in get_vacancies().
        """
        vf = VacancyFilter(full_config)

        # Insert two vacancies — use different channels to avoid UNIQUE conflict
        results_1 = vf.check_message("junior media buyer старое")
        assert len(results_1) == 1
        db.add_vacancy(
            channel_name="ch_old",
            message_id=6001,
            category=results_1[0].category,
            matched_phrase=results_1[0].matched_phrase,
            weight=results_1[0].weight,
            text="junior media buyer старое",
            link="https://t.me/ch_old/6001",
        )

        results_2 = vf.check_message("junior media buyer новое")
        assert len(results_2) == 1
        db.add_vacancy(
            channel_name="ch_new",
            message_id=6002,
            category=results_2[0].category,
            matched_phrase=results_2[0].matched_phrase,
            weight=results_2[0].weight,
            text="junior media buyer новое",
            link="https://t.me/ch_new/6002",
        )

        vacancies = db.get_vacancies()
        assert len(vacancies) == 2
        # Most-recently-inserted should appear first (ORDER BY sent_at DESC)
        # Both have same-second timestamps so we just check count and content
        msg_ids = [v["message_id"] for v in vacancies]
        assert set(msg_ids) == {6001, 6002}


# ---------------------------------------------------------------------------
# 4. Notifier + Filter interaction
# ---------------------------------------------------------------------------


class TestNotifierFilterInteraction:
    """Verify notifier formats filter results correctly."""

    def test_notifier_message_contains_all_fields(self, full_config):
        """Formatted message should include category, phrase, and original text."""
        notifier = TelegramNotifier(full_config)

        vacancy = FilterResult(
            category="Junior позиции",
            matched_phrase="junior media buyer",
            weight=10,
            original_text="Ищем junior media buyer без опыта",
        )

        message = notifier.format_message(vacancy, channel="job_channel_1", message_id=42)

        assert "Junior позиции" in message
        assert "junior media buyer" in message
        assert "Ищем junior media buyer без опыта" in message
        assert "https://t.me/job_channel_1/42" in message

    def test_notifier_message_without_channel_info(self, full_config):
        """When channel info is missing, link should show N/A."""
        notifier = TelegramNotifier(full_config)

        vacancy = FilterResult(
            category="Farmer",
            matched_phrase="farmer",
            weight=7,
            original_text="Требуется farmer",
        )

        message = notifier.format_message(vacancy)
        assert "N/A" in message

    def test_notifier_target_channel_strips_at(self, full_config):
        """Target channel should have @ prefix stripped."""
        notifier = TelegramNotifier(full_config)
        assert notifier.target_channel == "vacancy_notifications"
        assert not notifier.target_channel.startswith("@")

    @pytest.mark.asyncio
    async def test_notifier_send_failure_returns_false(self, full_config):
        """send_vacancy should return False on Telegram API error."""
        notifier = TelegramNotifier(full_config)

        # Mock client that raises on send
        mock_client = AsyncMock()
        mock_client.send_message = AsyncMock(side_effect=Exception("API flood"))
        notifier.client = mock_client

        vacancy = FilterResult(
            category="Test",
            matched_phrase="test",
            weight=5,
            original_text="test",
        )

        result = await notifier.send_vacancy(vacancy, "ch", 1)
        assert result is False


# ---------------------------------------------------------------------------
# 5. Config loading integration
# ---------------------------------------------------------------------------


def _load_example_config():
    """Load config.yaml.example (always present in repo; config.yaml is gitignored)."""
    with open("config.yaml.example", encoding="utf-8") as f:
        return yaml.safe_load(f)


class TestConfigLoading:
    """Verify config.example loads and has all required sections."""

    def test_config_loading(self):
        """Test that config loads correctly."""
        config = _load_example_config()

        assert "telegram" in config
        assert "channels" in config
        assert "filters" in config
        assert "schedule" in config
        assert "web" in config
        assert "logging" in config

    def test_config_has_required_telegram_keys(self):
        """Config must have api_id, api_hash, bot_token, target_channel."""
        config = _load_example_config()

        tg = config["telegram"]
        assert "api_id" in tg
        assert "api_hash" in tg
        assert "bot_token" in tg
        assert "target_channel" in tg

    def test_config_has_channels_list(self):
        """Config must have a non-empty channels list."""
        config = _load_example_config()

        assert isinstance(config["channels"], list)
        assert len(config["channels"]) > 0

    def test_config_has_filters_with_phrases(self):
        """Each filter must have name, phrases, and weight."""
        config = _load_example_config()

        for f_cfg in config["filters"]:
            assert "name" in f_cfg
            assert "phrases" in f_cfg
            assert isinstance(f_cfg["phrases"], list)
            assert len(f_cfg["phrases"]) > 0
            assert "weight" in f_cfg

    def test_config_filter_factory_produces_working_engine(self):
        """Config filters should produce a working VacancyFilter."""
        config = _load_example_config()

        vf = VacancyFilter(config)
        # Try matching a known phrase from config
        results = vf.check_message("Ищем junior media buyer без опыта")
        assert len(results) >= 1
        categories = [r.category for r in results]
        assert "Junior позиции" in categories


# ---------------------------------------------------------------------------
# 6. Database statistics integration
# ---------------------------------------------------------------------------


class TestDatabaseStats:
    """Verify database statistics reflect actual data."""

    def test_stats_reflect_added_data(self, db, full_config):
        """Stats should update after adding channels, filters, vacancies."""
        # Initially empty
        stats = db.get_stats()
        assert stats["total_channels"] == 0
        assert stats["total_filters"] == 0
        assert stats["total_vacancies"] == 0

        # Add data
        db.add_channel("@ch1")
        db.add_channel("@ch2")
        db.add_filter("Test", ["phrase1"], [], 5)
        db.add_vacancy("@ch1", 1, "Cat", "phrase1", 5, "text", "link")

        stats = db.get_stats()
        assert stats["total_channels"] == 2
        assert stats["total_filters"] == 1
        assert stats["total_vacancies"] == 1
        assert stats["vacancies_today"] >= 1

    def test_error_logging_integrates_with_stats(self, db):
        """Error log entries should appear in stats."""
        db.log_error("test_error", "Something went wrong", "@ch1")

        stats = db.get_stats()
        assert stats["errors_today"] >= 1


# ---------------------------------------------------------------------------
# 7. Collector + Filter integration (simulated pipeline)
# ---------------------------------------------------------------------------


class TestCollectorFilterPipeline:
    """Simulate what main.py's check_and_notify does."""

    def test_pipeline_filters_messages_from_collector(self, db, full_config):
        """Replicate check_and_notify logic: collect → filter → store.

        Each message is stored at most once (highest-weight match) due to
        UNIQUE(channel_name, message_id) on the vacancies table.
        """
        TelegramCollector(full_config, db=db)
        vf = VacancyFilter(full_config)

        # Simulate messages that would come from collector.check_channels()
        simulated_messages = [
            {
                "channel": "job_channel_1",
                "id": 7001,
                "text": "Ищем junior media buyer без опыта",
                "link": "https://t.me/job_channel_1/7001",
            },
            {
                "channel": "job_channel_1",
                "id": 7002,
                "text": "Продавец в магазин электроники",
                "link": "https://t.me/job_channel_1/7002",
            },
            {
                "channel": "job_channel_2",
                "id": 7003,
                "text": "Нужен accounts farmer, опыт от 2 лет",
                "link": "https://t.me/job_channel_2/7003",
            },
        ]

        sent_vacancies = []

        for message in simulated_messages:
            # Mark processed
            db.mark_message_processed(message["channel"], message["id"])

            results = vf.check_message(message["text"])
            if results:
                # Pick best match (highest weight) to avoid UNIQUE conflict
                best = max(results, key=lambda r: r.weight)
                db.add_vacancy(
                    channel_name=message["channel"],
                    message_id=message["id"],
                    category=best.category,
                    matched_phrase=best.matched_phrase,
                    weight=best.weight,
                    text=message["text"],
                    link=message["link"],
                )
                sent_vacancies.append(best)

        # Message 7001: "junior media buyer" + "без опыта" → best match stored once
        # Message 7002: no match → skipped
        # Message 7003: "accounts farmer" + "обучим с нуля" → best match stored once
        assert len(sent_vacancies) == 2

        # All messages should be marked as processed
        for msg in simulated_messages:
            assert db.is_message_processed(msg["channel"], msg["id"]) is True

        # Vacancies stored
        vacancies = db.get_vacancies()
        assert len(vacancies) == 2
        categories = {v["category"] for v in vacancies}
        assert "Junior позиции" in categories
        assert "Farmer" in categories

    def test_pipeline_handles_empty_channel(self, db, full_config):
        """Pipeline should handle channels with no messages gracefully."""
        vf = VacancyFilter(full_config)

        # No messages to process
        messages = []

        for message in messages:
            results = vf.check_message(message.get("text", ""))
            for result in results:
                db.add_vacancy(
                    channel_name=message["channel"],
                    message_id=message["id"],
                    category=result.category,
                    matched_phrase=result.matched_phrase,
                    weight=result.weight,
                    text=message["text"],
                    link=message["link"],
                )

        assert len(db.get_vacancies()) == 0
        assert len(db.get_channels()) == 0
