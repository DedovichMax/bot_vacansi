# Task 4: Filter Engine — Отчёт

**Статус:** DONE
**Коммит:** `86094fe` — feat: add filter engine with exact phrase matching and exclusion support

## Что сделано

Создан фильтр вакансий, который сопоставляет текстовые сообщения с настроенными фильтрами (подстроки-фразы) с поддержкой:

- Точного совпадения фраз (substring match, регистронезависимый)
- Исключающих слов (exclude) — еслиexclude-фраза найдена, фильтр пропускает категорию
- Множественных совпадений — сообщение может совпасть с несколькими категориями
- Веса (weight) — каждый фильтр имеет числовую весовую категорию

## Файлы

| Файл | Описание |
|------|----------|
| `filter/vacancy_filter.py` | Класс `VacancyFilter` + dataclass `FilterResult` |
| `tests/test_filter.py` | 6 тестов, покрывающих все критерии |

## TDD Evidence

### RED — Тесты падают (до реализации)

```
ERROR collecting tests/test_filter.py
E   ModuleNotFoundError: No module named 'filter.vacancy_filter'
```

### GREEN — Все тесты проходят (после реализации)

```
tests/test_filter.py::test_filter_exact_phrase_match PASSED
tests/test_filter.py::test_filter_no_match_on_partial PASSED
tests/test_filter.py::test_filter_exclude_words PASSED
tests/test_filter.py::test_filter_multiple_matches PASSED
tests/test_filter.py::test_filter_case_insensitive PASSED
tests/test_filter.py::test_filter_with_filter_config PASSED
6 passed
```

### Full suite — все 13 тестов ( Tasks 1-4)

```
13 passed in 0.12s
```

## Архитектура

```python
@dataclass
class FilterResult:
    category: str          # Имя фильтра
    matched_phrase: str    # Какая фраза совпала
    weight: int            # Вес фильтра
    original_text: str     # Оригинальный текст

class VacancyFilter:
    check_message(text) -> List[FilterResult]
    _has_exclude_word(text, exclude_words) -> bool
    _find_phrase_match(text, phrases) -> str | None
```

## Concerns / Замечания

Нет. Всё работает по плану, все тесты проходят, нет side effects на предыдущие задачи.
