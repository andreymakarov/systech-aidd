ADR-010: SQLite + async SQLAlchemy ORM + Alembic for persistence

Status
Accepted

Context
We need persistent conversation history with soft delete and message metadata while keeping KISS and conforming to project conventions: async I/O, DI, one class per file, strict typing.

Decision
- Use SQLite (file) with async SQLAlchemy ORM (sqlite+aiosqlite)
- Manage schema via Alembic (async env with render_as_batch=True for SQLite)
- Implement soft delete (deleted_at), and store created_at (ISO8601) and length
- Provide session_factory to ConversationManager via DI
- Expose history as list of dicts including metadata; handlers strip metadata before LLM

Consequences
- No blocking I/O in event loop
- Simple local deployment and Docker packaging
- Future migrations handled by Alembic

Schema
- messages(id PK, user_id INT, role TEXT, content TEXT, length INT, created_at TEXT, deleted_at TEXT NULL)
- Index: (user_id, deleted_at)



