from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .content import ContentItem, canonical_json, load_seed, seed_summary
from .db import Database, utc_now
from .rules import RULES
from .settings import SEED_PATH


class SeedConflictError(RuntimeError):
    pass


def import_seed(database: Database, path: Path = SEED_PATH) -> dict[str, Any]:
    document, items = load_seed(path)
    database.migrate()
    now = utc_now()
    inserted = 0
    unchanged = 0
    with database.transaction(write=True) as session:
        for item in items:
            existing = session.row(session.execute(
                'SELECT sha256 FROM content_items WHERE id=? AND version=?', (item.id, item.version)
            ))
            if existing:
                if existing['sha256'] != item.sha256:
                    raise SeedConflictError(
                        f"{item.id} v{item.version} уже существует с другим содержимым; версии неизменяемы, добавьте новую version."
                    )
                unchanged += 1
                continue
            row = item
            session.execute(
                '''INSERT INTO content_items
                (id, version, block_type, text, scope, topics_json, allowed_signs_json,
                 required_rule_ids_json, forbidden_rule_ids_json, allowed_tones_json,
                 min_gap_days, review_status, notes, word_count, sha256, raw_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (row.id, row.version, row.block_type, row.text, row.scope,
                 canonical_json(row.topics), canonical_json(row.allowed_signs),
                 canonical_json(row.required_rule_ids), canonical_json(row.forbidden_rule_ids),
                 canonical_json(row.allowed_tones), row.min_gap_days, row.review_status, row.notes,
                 row.word_count, row.sha256, canonical_json(row.raw), now, now),
            )
            inserted += 1

        for rule_id, definition in RULES.items():
            raw = canonical_json(definition)
            digest = hashlib.sha256(raw.encode('utf-8')).hexdigest()
            existing = session.row(session.execute(
                'SELECT sha256 FROM rule_versions WHERE rule_id=? AND version=?',
                (rule_id, definition['version']),
            ))
            if existing and existing['sha256'] != digest:
                raise SeedConflictError(f'{rule_id} v{definition["version"]} изменено без увеличения версии.')
            if not existing:
                session.execute(
                    'INSERT INTO rule_versions(rule_id, version, definition_json, sha256, created_at) VALUES (?, ?, ?, ?, ?)',
                    (rule_id, definition['version'], raw, digest, now),
                )

        source_sha = hashlib.sha256(path.read_bytes()).hexdigest()
        session.execute(
            '''INSERT INTO seed_imports(source_name, schema_version, source_sha256, imported_at)
            VALUES (?, ?, ?, ?) ON CONFLICT DO NOTHING''',
            (path.name, document['schema_version'], source_sha, now),
        )

    return {
        'source': str(path), 'source_sha256': source_sha, 'inserted': inserted,
        'unchanged': unchanged, 'rules_versioned': len(RULES), **seed_summary(items),
    }


def content_rows(session: Any, *, approved_only: bool = True) -> list[dict[str, Any]]:
    where = "WHERE review_status='approved'" if approved_only else ''
    return session.rows(session.execute(f'SELECT * FROM content_items {where} ORDER BY block_type, id, version'))


def seed_report(database: Database) -> dict[str, Any]:
    database.migrate()
    with database.transaction() as session:
        rows = content_rows(session, approved_only=False)
    items: list[ContentItem] = []
    for row in rows:
        raw = json.loads(row['raw_json'])
        items.append(ContentItem(
            id=row['id'], version=row['version'], block_type=row['block_type'], text=row['text'],
            scope=row['scope'], topics=tuple(json.loads(row['topics_json'])),
            allowed_signs=tuple(json.loads(row['allowed_signs_json'])),
            required_rule_ids=tuple(json.loads(row['required_rule_ids_json'])),
            forbidden_rule_ids=tuple(json.loads(row['forbidden_rule_ids_json'])),
            allowed_tones=tuple(json.loads(row['allowed_tones_json'])), min_gap_days=row['min_gap_days'],
            review_status=row['review_status'], notes=row['notes'], word_count=row['word_count'],
            sha256=row['sha256'], raw=raw,
        ))
    return seed_summary(items)
