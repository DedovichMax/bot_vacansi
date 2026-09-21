# Task 8: Web Panel — Report

## What Was Implemented

Full web panel for the Telegram Vacancy Bot using FastAPI + Jinja2 + HTTP Basic Auth.

### Files Created
| File | Purpose |
|------|---------|
| `web/auth.py` | HTTP Basic Auth dependency with constant-time credential comparison (`secrets.compare_digest`) |
| `web/templates/index.html` | Dashboard HTML with stats cards, channel/filter/vacancy tables, and delete buttons |

### Files Expanded (from Task 7 stubs)
| File | Change |
|------|--------|
| `web/app.py` | Expanded from 23-line health-only stub to full app with `app.state.db`, `app.state.web_config`, Jinja2 template rendering, and auth-protected index route |
| `web/routes.py` | Expanded from 4-line empty router stub to full REST API with 9 endpoints |

### Test File
| File | Tests |
|------|-------|
| `tests/test_web.py` | 19 tests covering auth, all CRUD endpoints, stats, HTML rendering |

## TDD Evidence

### RED State (15 failed, 4 passed)
```
tests/test_web.py::test_auth_rejects_wrong_credentials FAILED  (404 == 401)
tests/test_web.py::test_auth_accepts_correct_credentials FAILED (404 == 200)
tests/test_web.py::test_auth_api_endpoints_require_auth FAILED  (404 == 401)
tests/test_web.py::test_get_channels_empty FAILED               (404 == 200)
tests/test_web.py::test_add_channel FAILED                      (404 == 200)
tests/test_web.py::test_add_channel_missing_name FAILED         (404 == 400)
tests/test_web.py::test_delete_channel FAILED                   (KeyError: 'id')
tests/test_web.py::test_get_filters_empty FAILED                (404 == 200)
tests/test_web.py::test_add_filter FAILED                       (404 == 200)
tests/test_web.py::test_add_filter_missing_name FAILED          (404 == 400)
tests/test_web.py::test_delete_filter FAILED                    (KeyError: 'id')
tests/test_web.py::test_get_vacancies_empty FAILED              (404 == 200)
tests/test_web.py::test_get_vacancies_after_add FAILED          (404 == 200)
tests/test_web.py::test_get_stats FAILED                        (404 == 200)
tests/test_web.py::test_index_page FAILED                       (404 == 200)
```

All 15 failures were 404s because routes/auth/index didn't exist yet.

### GREEN State (19 passed, 0 failed, 0 warnings)
```
tests/test_web.py::test_health_endpoint                     PASSED
tests/test_web.py::test_auth_rejects_wrong_credentials      PASSED
tests/test_web.py::test_auth_accepts_correct_credentials    PASSED
tests/test_web.py::test_auth_api_endpoints_require_auth     PASSED
tests/test_web.py::test_get_channels_empty                  PASSED
tests/test_web.py::test_add_channel                         PASSED
tests/test_web.py::test_add_channel_missing_name            PASSED
tests/test_web.py::test_delete_channel                      PASSED
tests/test_web.py::test_delete_channel_not_found            PASSED
tests/test_web.py::test_get_filters_empty                   PASSED
tests/test_web.py::test_add_filter                          PASSED
tests/test_web.py::test_add_filter_missing_name             PASSED
tests/test_web.py::test_delete_filter                       PASSED
tests/test_web.py::test_delete_filter_not_found             PASSED
tests/test_web.py::test_get_vacancies_empty                 PASSED
tests/test_web.py::test_get_vacancies_after_add             PASSED
tests/test_web.py::test_stats                               PASSED
tests/test_web.py::test_index_page                          PASSED
tests/test_web.py::test_create_app_returns_fastapi          PASSED
```

### Full Suite (48 passed, 0 failed)
All existing tests from Tasks 1-7 continue to pass.

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Health check |
| GET | `/` | Yes | Dashboard HTML page |
| GET | `/api/channels` | Yes | List all channels |
| POST | `/api/channels` | Yes | Add channel |
| DELETE | `/api/channels/{id}` | Yes | Delete channel |
| GET | `/api/filters` | Yes | List all filters |
| POST | `/api/filters` | Yes | Add filter |
| DELETE | `/api/filters/{id}` | Yes | Delete filter |
| GET | `/api/vacancies` | Yes | List vacancies |
| GET | `/api/stats` | Yes | Dashboard statistics |

## Architecture Decisions

- **Auth via `app.state`**: Config and DB are stored in `app.state` and accessed via `request.app.state` in route dependencies. This avoids global state and keeps the `create_app(db, config)` interface clean.
- **Constant-time auth**: `secrets.compare_digest` prevents timing attacks on credential comparison.
- **TemplateResponse fixed**: Used the new Starlette API `TemplateResponse(request, name, context)` to avoid deprecation warning.

## Commit

```
12c1ca8 feat(web): add web panel with FastAPI, Basic Auth, and Jinja2 dashboard
```
