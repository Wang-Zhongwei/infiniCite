# AGENTS.md

## Cursor Cloud specific instructions

### Project Overview

infiniCite is an academic paper knowledge base and visualization platform built with Django 4.2 (Python 3.11), PostgreSQL, Elasticsearch 7.x, and HuggingFace SPECTER2 for semantic search.

### Required Services

| Service | How to start | Notes |
|---|---|---|
| PostgreSQL 16 | `sudo pg_ctlcluster 16 main start` | Must be running before Django. DB: `infinicite`, user/pass: `infinicite/infinicite` |
| Elasticsearch 7.17 | `ES_JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64 /opt/elasticsearch/bin/elasticsearch -d -p /tmp/es.pid` | Must be running before Django. Verify with `curl http://localhost:9200/` |
| Django dev server | `cd /workspace && source .venv/bin/activate && python manage.py runserver 0.0.0.0:8000` | Serves on port 8000 |

### Config Files

The `config/` directory is gitignored and must exist with these files for Django to start:
- `config/__init__.py` (empty)
- `config/db_config.py` — PostgreSQL `DATABASES` dict
- `config/django_config.py` — Django `SECRET_KEY`
- `config/elastic_config.py` — `ELASTICSEARCH_DSL` dict pointing to ES
- `config/api_keys.py` — `OPENAI_API_KEY` (can be placeholder for non-NL-search dev)

### Important Gotchas

- **SPECTER2 model loads at import time**: `infiniCite/specter.py` downloads and loads `allenai/specter2_base` + `allenai/specter2_adhoc_query` adapter on first run. This is imported by `paper/views.py`. The model is cached in `~/.cache/huggingface/` after first download (~440 MB).
- **Elasticsearch must be reachable at startup**: `settings.py` creates an `Elasticsearch` client at import time. If ES is down, Django won't start.
- **PostgreSQL ArrayField**: The project uses `django.contrib.postgres.fields.ArrayField`, so SQLite cannot be used as a substitute database.
- **Test suite has pre-existing failures**: 4 of 5 tests in `paper/tests.py` fail because the test client is not authenticated before making requests that require login. This is a pre-existing issue, not caused by environment setup.
- **DB user needs CREATEDB**: The PostgreSQL user needs `CREATEDB` permission to run `python manage.py test` (Django creates a test database).

### Lint & Test Commands

- Lint: `python -m black --check .` (project uses black; many files are not yet formatted)
- Tests: `python manage.py test` (ensure PostgreSQL and Elasticsearch are running first)
- Dev server: `python manage.py runserver 0.0.0.0:8000`
