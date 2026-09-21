# tests/test_filter.py
import pytest

from filter.vacancy_filter import VacancyFilter


@pytest.fixture
def filter_config():
    return {
        "filters": [
            {
                "name": "Junior позиции",
                "phrases": ["junior media buyer", "junior medua buyer", "младший медиабайер"],
                "exclude": ["senior junior"],
                "weight": 10,
            },
            {
                "name": "Без опыта",
                "phrases": ["без опыта", "для начинающих", "обучим с нуля"],
                "exclude": [],
                "weight": 8,
            },
        ]
    }


def test_filter_exact_phrase_match():
    """Test that filter matches exact phrases."""
    config = {
        "filters": [{"name": "Test", "phrases": ["junior media buyer"], "exclude": [], "weight": 5}]
    }
    vf = VacancyFilter(config)

    message_text = "Ищем junior media buyer без опыта"
    results = vf.check_message(message_text)

    assert len(results) == 1
    assert results[0].category == "Test"
    assert results[0].matched_phrase == "junior media buyer"


def test_filter_no_match_on_partial():
    """Test that filter doesn't match partial words."""
    config = {
        "filters": [{"name": "Test", "phrases": ["junior media buyer"], "exclude": [], "weight": 5}]
    }
    vf = VacancyFilter(config)

    # "junior" alone should not match "junior media buyer"
    message_text = "Требуется junior разработчик"
    results = vf.check_message(message_text)

    assert len(results) == 0


def test_filter_exclude_words():
    """Test that exclude words prevent matching."""
    config = {
        "filters": [
            {
                "name": "Test",
                "phrases": ["junior media buyer"],
                "exclude": ["senior junior"],
                "weight": 5,
            }
        ]
    }
    vf = VacancyFilter(config)

    message_text = "senior junior media buyer"
    results = vf.check_message(message_text)

    assert len(results) == 0


def test_filter_multiple_matches():
    """Test that filter can match multiple phrases from different categories."""
    config = {
        "filters": [
            {"name": "Junior", "phrases": ["junior media buyer"], "exclude": [], "weight": 10},
            {"name": "Без опыта", "phrases": ["без опыта"], "exclude": [], "weight": 8},
        ]
    }
    vf = VacancyFilter(config)

    message_text = "junior media buyer без опыта"
    results = vf.check_message(message_text)

    assert len(results) == 2
    categories = [r.category for r in results]
    assert "Junior" in categories
    assert "Без опыта" in categories


def test_filter_case_insensitive():
    """Test that filter is case insensitive."""
    config = {
        "filters": [{"name": "Test", "phrases": ["junior media buyer"], "exclude": [], "weight": 5}]
    }
    vf = VacancyFilter(config)

    message_text = "JUNIOR MEDIA BUYER"
    results = vf.check_message(message_text)

    assert len(results) == 1


def test_filter_with_filter_config(filter_config):
    """Test filter with full config."""
    vf = VacancyFilter(filter_config)

    # Should match
    results = vf.check_message("Ищем junior media buyer без опыта")
    assert len(results) == 2

    # Should not match (exclude)
    results = vf.check_message("senior junior media buyer")
    assert len(results) == 0
