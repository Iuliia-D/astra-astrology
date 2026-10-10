from __future__ import annotations

import json
from typing import Any

from .content import SIGNS, canonical_json, load_seed, seed_summary
from .db import Database
from .settings import SEED_PATH


def verify_database(database: Database) -> dict[str, Any]:
    database.migrate()
    with database.transaction() as session:
        content = session.rows(session.execute('SELECT * FROM content_items ORDER BY id, version'))
        forecasts = session.rows(session.execute("SELECT * FROM published_forecasts WHERE status='published' ORDER BY forecast_date, sign"))
        block_rows = session.rows(session.execute(
            '''SELECT fb.forecast_id, fb.block_type, ci.id, ci.version, ci.scope, ci.review_status
            FROM forecast_blocks fb JOIN content_items ci ON ci.id=fb.content_id AND ci.version=fb.content_version'''
        ))
        rules = session.rows(session.execute('SELECT rule_id, version FROM rule_versions'))
    issues: list[str] = []
    published_ids = {row['id'] for row in forecasts}
    block_map: dict[str, list[dict[str, Any]]] = {}
    for block in block_rows:
        block_map.setdefault(block['forecast_id'], []).append(block)
        if block['scope'] == 'test_only' or block['review_status'] != 'approved':
            issues.append(f"Запрещённый текст в публикации {block['forecast_id']}: {block['id']} v{block['version']}.")
    for forecast in forecasts:
        blocks = block_map.get(forecast['id'], [])
        if not any(block['block_type'] == 'main' for block in blocks):
            issues.append(f"У прогноза {forecast['forecast_date']}/{forecast['sign']} отсутствует main.")
        if forecast['sign'] not in SIGNS:
            issues.append(f"Неизвестный знак публикации: {forecast['sign']}.")
        payload = json.loads(forecast['export_json'])
        if payload.get('publication', {}).get('id') != forecast['id']:
            issues.append(f"ID экспорта не совпадает с записью {forecast['id']}.")
        selections = payload.get('publication', {}).get('content_selections', {})
        for block in blocks:
            exported = selections.get(block['block_type'], {})
            if exported.get('id') != block['id'] or exported.get('version') != block['version']:
                issues.append(f"Состав блока не совпадает для {forecast['id']}/{block['block_type']}.")
    seed_doc, seed_items = load_seed(SEED_PATH)
    summary = seed_summary(seed_items)
    stored_content = {(row['id'], row['version']): row for row in content}
    for item in seed_items:
        stored = stored_content.get((item.id, item.version))
        if stored is None:
            issues.append(f'В базе отсутствует seed-запись {item.id} v{item.version}.')
            continue
        if stored['sha256'] != item.sha256 or canonical_json(json.loads(stored['raw_json'])) != canonical_json(item.raw):
            issues.append(f'Seed-запись {item.id} v{item.version} отличается от утверждённого источника.')
    if issues:
        raise RuntimeError('\n'.join(issues))
    return {
        'content_version_count': len(content), 'published_forecast_count': len(forecasts),
        'forecast_block_count': len(block_rows), 'rule_version_count': len(rules),
        'seed_schema_version': seed_doc['schema_version'], 'seed': summary,
        'published_content_ids': len(block_rows), 'test_only_publications': 0,
    }
