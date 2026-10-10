from __future__ import annotations

import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import unquote

from .settings import DATABASE_URL, MIGRATIONS_PATH, ROOT


class Session:
    def __init__(self, connection: Any, postgres: bool):
        self.connection = connection
        self.postgres = postgres

    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> Any:
        if self.postgres:
            sql = sql.replace('?', '%s')
            cursor = self.connection.cursor()
            cursor.execute(sql, params)
            return cursor
        return self.connection.execute(sql, params)

    @staticmethod
    def row(cursor: Any) -> dict[str, Any] | None:
        row = cursor.fetchone()
        if row is None:
            return None
        if isinstance(row, sqlite3.Row):
            return dict(row)
        return dict(zip([column.name for column in cursor.description], row))

    @staticmethod
    def rows(cursor: Any) -> list[dict[str, Any]]:
        if isinstance(cursor, sqlite3.Cursor):
            return [dict(row) for row in cursor.fetchall()]
        names = [column.name for column in cursor.description]
        return [dict(zip(names, row)) for row in cursor.fetchall()]


class Database:
    def __init__(self, url: str | None = None):
        self.url = url or DATABASE_URL
        self.postgres = self.url.startswith(('postgres://', 'postgresql://', 'postgresql+psycopg://'))
        if not self.postgres and not self.url.startswith('sqlite:///'):
            raise ValueError('DATABASE_URL должен быть PostgreSQL или sqlite:/// для тестов.')
        self.sqlite_path: str | None = None
        if not self.postgres:
            value = unquote(self.url.removeprefix('sqlite:///'))
            if value == ':memory:':
                self.sqlite_path = value
            else:
                path = Path(value)
                if not path.is_absolute():
                    path = ROOT / path
                path.parent.mkdir(parents=True, exist_ok=True)
                self.sqlite_path = str(path)

    @contextmanager
    def transaction(self, *, write: bool = False, lock_key: str | None = None) -> Iterator[Session]:
        if self.postgres:
            try:
                import psycopg
            except ImportError as exc:
                raise RuntimeError('Для PostgreSQL установите backend requirements.') from exc
            url = self.url.replace('postgres://', 'postgresql://', 1).replace('postgresql+psycopg://', 'postgresql://', 1)
            connection = psycopg.connect(url)
            try:
                with connection.cursor() as cursor:
                    if lock_key:
                        cursor.execute('SELECT pg_advisory_xact_lock(hashtext(%s))', (lock_key,))
                yield Session(connection, True)
                connection.commit()
            except Exception:
                connection.rollback()
                raise
            finally:
                connection.close()
            return

        assert self.sqlite_path is not None
        connection = sqlite3.connect(self.sqlite_path, timeout=30, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute('PRAGMA foreign_keys = ON')
        connection.execute('PRAGMA busy_timeout = 30000')
        try:
            connection.execute('BEGIN IMMEDIATE' if write else 'BEGIN')
            yield Session(connection, False)
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def migrate(self) -> list[str]:
        migration_files = sorted(MIGRATIONS_PATH.glob('*.sql'))
        with self.transaction(write=True) as session:
            session.execute('CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY, applied_at TEXT NOT NULL)')
            applied = {row['version'] for row in session.rows(session.execute('SELECT version FROM schema_migrations'))}
            for path in migration_files:
                if path.name in applied:
                    continue
                sql = path.read_text(encoding='utf-8')
                statements = [part.strip() for part in re.split(r';\s*(?:\n|$)', sql) if part.strip()]
                for statement in statements:
                    session.execute(statement)
                session.execute('INSERT INTO schema_migrations(version, applied_at) VALUES (?, ?)', (path.name, utc_now()))
                applied.add(path.name)
        return sorted(applied)


def utc_now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat(timespec='seconds')
