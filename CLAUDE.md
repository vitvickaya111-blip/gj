# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Telegram bot template with a FastAPI backend service. The project uses:
- **aiogram 3.x** for Telegram bot functionality
- **FastAPI** for REST API service
- **SQLAlchemy 2.0** with async support for database operations
- **PostgreSQL** as the primary database
- **Redis** for caching and rate limiting
- **Alembic** for database migrations
- **Docker Compose** for containerized deployment
- **Poetry** for Python dependency management

## Development Setup

### Initial Setup

1. Install dependencies using Poetry:
   ```bash
   poetry install
   poetry shell
   ```

2. Create `.env` file at project root based on environment templates in `docker/` directory (`.env.dev`, `.env.prod`, `.env.test`)

3. Start Docker services:
   ```bash
   docker compose -f docker/dev.yml up -d
   ```

### Running Services Locally

**Run Telegram Bot:**
```bash
cd backend
python -m bot.main
```

**Run FastAPI Service:**
```bash
cd backend/api
uvicorn src.main:app --reload
# or
python -m src.main
```

### Database Migrations

**Create new migration:**
```bash
bash backend/scripts/alembic/create_migrations.sh
# This runs: docker exec bot alembic revision --autogenerate -m "<message>"
```

**Apply migrations:**
```bash
bash backend/scripts/alembic/run_migrations.sh
# This runs: docker exec bot alembic upgrade head
```

**Direct alembic commands (if not using Docker):**
```bash
cd backend
alembic upgrade head
alembic revision --autogenerate -m "migration message"
```

### Testing

```bash
pytest ./tests
```

## Architecture Overview

### Project Structure

```
backend/
├── api/              # FastAPI REST API service
│   └── src/
│       ├── users/    # User endpoints (versioned as v1/)
│       ├── common/   # Shared schemas and utilities
│       └── main.py   # FastAPI app initialization
├── bot/              # Telegram bot (aiogram)
│   ├── handlers/     # Message handlers (admin, user, channel, errors)
│   ├── middlewares/  # Bot middlewares (config, database, i18n)
│   ├── keyboards/    # Reply and inline keyboards
│   ├── filters/      # Custom filters (e.g., admin filter)
│   ├── services/     # Bot services (broadcaster, scheduler)
│   ├── utils/        # Bot utilities (states, commands, tools)
│   ├── locales/      # i18n translations (default: Russian)
│   └── main.py       # Bot entry point
├── infrastructure/
│   ├── database/     # Database layer
│   │   ├── models/   # SQLAlchemy models
│   │   ├── repo/     # Repository pattern implementation
│   │   └── setup.py  # Database engine and session setup
│   ├── migrations/   # Alembic migrations
│   └── api_services/ # API utilities (CORS, cache, exceptions)
└── settings/         # Configuration modules using pydantic-settings
```

### Configuration System

Settings are loaded via **pydantic-settings** from environment variables with nested delimiter `__`:
- `backend/settings/app_settings.py` - Main settings aggregator
- Individual settings modules: `bot_settings.py`, `db_settings.py`, `redis_settings.py`, `logging_settings.py`, `miscellaneous_settings.py`
- Access via: `from settings import settings` or `from settings.app_settings import get_app_settings()`
- Environment variables use double underscore for nesting: `POSTGRES__DB_USER`, `POSTGRES__DB_PASSWORD`

### Database Layer

**Repository Pattern:**
- Base repository in `infrastructure/database/repo/base.py` provides CRUD operations
- Model-specific repositories extend `BaseRepo` (e.g., `repo/users.py`)
- All repos use async SQLAlchemy with `async_sessionmaker`
- Database setup: `infrastructure/database/setup.py` manages engine and session pool

**Key Methods in BaseRepo:**
- `get(obj_id)` - Fetch single object
- `create(**kwargs)` - Insert new record
- `create_on_conflict_do_nothing(**kwargs)` - Upsert pattern
- `update(obj_id, **kwargs)` - Update records (supports single ID or list)
- `delete(obj_id)` - Delete records (supports single ID or list)
- `get_all(limit, offset, user_id)` - Fetch all with pagination
- `count_all()` - Count all records

### Bot Architecture (aiogram)

**Main Entry Point:** `backend/bot/main.py`
- Uses `MemoryStorage()` for FSM state
- Initializes `AsyncIOScheduler` for scheduled tasks
- Configures i18n with locales in `backend/bot/locales/` (default: Russian)
- Registers global middlewares: `ConfigMiddleware`, `DatabaseMiddleware`, `CustomI18nMiddleware`

**Middleware Layers:**
- Applied to messages, callback queries, and chat member updates
- Channel posts use only `ConfigMiddleware`
- Middlewares inject: settings, scheduler, database session, Redis, i18n

**Handler Organization:**
- `handlers/user/` - User interactions (start command, etc.)
- `handlers/admin/` - Admin-only commands (filtered by admin filter)
- `handlers/channel/` - Channel post handlers
- `handlers/errors/` - Error handling for bot API errors

**Utilities:**
- `utils/set_bot_commands.py` - Sets bot commands for users and admins
- `utils/states.py` - FSM state definitions
- `services/broadcaster.py` - Broadcast messages to users
- `services/sheduler.py` - Scheduled tasks

### API Architecture (FastAPI)

**Main Entry Point:** `backend/api/src/main.py`
- Uses `ORJSONResponse` for JSON serialization
- Implements lifespan context manager for startup/shutdown
- Integrates: Redis caching (`fastapi-cache2`), rate limiting (`fastapi-limiter`), pagination (`fastapi-pagination`)
- CORS setup via `infrastructure/api_services/common/cors.py`

**Endpoints:**
- `/ping` - Health check
- `/version` - API version (cached for 600s)
- `/api/v1/users/*` - User operations (see `api/src/users/v1/user.py`)
- `/api/openapi` - Swagger docs
- `/api/openapi.json` - OpenAPI spec

**Database Integration:**
- Uses global `async_session` from `infrastructure/database/setup.py`
- Initialized in `initialize_database()` during lifespan startup
- Access via `RequestsRepo` or FastAPI dependency injection

### Docker Services

**dev.yml includes:**
- `nginx` - Reverse proxy (port 81:80)
- `bot` - Telegram bot container
- `api` - FastAPI service (port 8000:8000)
- `postgres` - PostgreSQL 15.3 (port 5432:5432)
- `redis` - Redis cache
- `dozzle` - Log viewer (port 8080:8080)

All services share `shared_network` bridge network.

## Important Patterns

### Adding New Bot Handlers
1. Create handler file in appropriate `backend/bot/handlers/` subdirectory
2. Define router with decorators (`@router.message`, `@router.callback_query`, etc.)
3. Register router in `backend/bot/handlers/__init__.py` by adding to `routers_list`
4. Bot will auto-include on startup via `dp.include_routers(*routers_list)`

### Adding New API Endpoints
1. Create endpoint module in `backend/api/src/<domain>/v<version>/`
2. Define router with FastAPI decorators
3. Import and include router in `backend/api/src/main.py` with prefix and tags
4. Use dependency injection for database access (see existing user endpoints)

### Database Models and Migrations
1. Define model in `backend/infrastructure/database/models/`
2. Import model in `backend/infrastructure/database/models/__init__.py`
3. Create repository extending `BaseRepo` in `backend/infrastructure/database/repo/`
4. Generate migration: `bash backend/scripts/alembic/create_migrations.sh`
5. Apply migration: `bash backend/scripts/alembic/run_migrations.sh`

### Environment Variables
- Environment files live in `docker/` directory: `.env.dev`, `.env.prod`, `.env.test`
- Use double underscore for nested settings: `POSTGRES__DB_NAME`, `BOT__TOKEN`
- Settings are type-validated via pydantic models in `backend/settings/`
