# tests/test_database.py
import os
import sqlite3

from utils.database import Database


def test_database_initialization():
    """Test that database creates all tables on init."""
    db_path = "tests/test.db"

    if os.path.exists(db_path):
        os.remove(db_path)

    Database(db_path)

    # Check tables exist
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    assert "channels" in tables
    assert "filters" in tables
    assert "vacancies" in tables
    assert "processed_messages" in tables
    assert "error_log" in tables

    # Cleanup
    os.remove(db_path)


def test_add_channel():
    """Test adding a channel to database."""
    db_path = "tests/test_add_channel.db"

    if os.path.exists(db_path):
        os.remove(db_path)

    db = Database(db_path)

    # Add channel
    channel_id = db.add_channel("@test_channel")
    assert channel_id is not None

    # Get channels
    channels = db.get_channels()
    assert len(channels) == 1
    assert channels[0]["channel_name"] == "@test_channel"
    assert channels[0]["is_active"]

    # Cleanup
    os.remove(db_path)


def test_add_filter():
    """Test adding a filter to database."""
    db_path = "tests/test_add_filter.db"

    if os.path.exists(db_path):
        os.remove(db_path)

    db = Database(db_path)

    # Add filter
    filter_id = db.add_filter(
        name="Test Filter",
        phrases=["test phrase", "another phrase"],
        exclude=["exclude me"],
        weight=5,
    )
    assert filter_id is not None

    # Get filters
    filters = db.get_filters()
    assert len(filters) == 1
    assert filters[0]["name"] == "Test Filter"

    # Cleanup
    os.remove(db_path)


def test_add_vacancy():
    """Test adding a vacancy to database."""
    db_path = "tests/test_add_vacancy.db"

    if os.path.exists(db_path):
        os.remove(db_path)

    db = Database(db_path)

    # Add vacancy
    vacancy_id = db.add_vacancy(
        channel_name="@test_channel",
        message_id=12345,
        category="Test Category",
        matched_phrase="test phrase",
        weight=5,
        text="Test vacancy text",
        link="https://t.me/test/12345",
    )
    assert vacancy_id is not None

    # Get vacancies
    vacancies = db.get_vacancies()
    assert len(vacancies) == 1
    assert vacancies[0]["channel_name"] == "@test_channel"

    # Cleanup
    os.remove(db_path)


def test_is_message_processed():
    """Test duplicate detection."""
    db_path = "tests/test_duplicate.db"

    if os.path.exists(db_path):
        os.remove(db_path)

    db = Database(db_path)

    # Message not processed yet
    assert not db.is_message_processed("@channel", 12345)

    # Mark as processed
    db.mark_message_processed("@channel", 12345)

    # Now it's processed
    assert db.is_message_processed("@channel", 12345)

    # Different message still not processed
    assert not db.is_message_processed("@channel", 12346)

    # Cleanup
    os.remove(db_path)
