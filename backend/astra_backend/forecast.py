from __future__ import annotations

import hashlib
import json
import uuid
from datetime import date, datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

from .content import SIGNS, canonical_json
from .db import Database, utc_now
from .rules import RULES_VERSION, context_for_sign
from .selector import insert_assignment, recommendation_conflict, select_content
from .settings import TIMEZONE

ALGORITHM_VERSION = 'astra-forecast-v1'
MONTHS_RU = ('января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря')
BLOCK_ORDER = ('main', 'accent', 'love', 'career', 'energy', 'finance', 'do', 'avoid', 'notice')
METRIC_LABELS = {'love': ('Любовь', 'violet'), 'career': ('Работа', 'blue'), 'energy': ('Энергия', 'cyan'), 'finance': ('Финансы', 'violet')}
BLOCK_TOPICS = {
    'love': {'relationships', 'values', 'comfort', 'attraction', 'partnerships', 'agreements', 'romance'},
    'career': {'career', 'work', 'responsibility', 'discipline', 'long_term_tasks', 'goals', 'daily_duties'},
    'energy': {'emotions', 'habits', 'daily_needs', 'action', 'daily_duties', 'routine'},
    'finance': {'money', 'personal_resources', 'values', 'shared_finances', 'obligations', 'shared_resources'},
}


class PublishedForecastExists(RuntimeError):
    pass


class RequiredContentMissing(RuntimeError):
    pass


class _PreviewResult(Exception):
    def __init__(self, export: dict[str, Any]):
        self.export = export


def display_date(value: date) -> str:
    return f'{value.day} {MONTHS_RU[value.month - 1]} {value.year}'


def _find_event_for_block(event_rows: list[dict[str, Any]], block: str) -> dict[str, Any] | None:
    if block not in {'key_moment', 'event_summary'}:
        return None
    for event in event_rows:
        meaning = event.get('interpretation') or {}
        if event.get('exact_time_utc') and block in meaning.get('permitted_block_types', ()):
            if block == 'event_summary' and event.get('site_slug'):
                return event
            if block == 'key_moment':
                return event
    return None


def build_forecast(
    database: Database,
    *,
    forecast_date: date,
    sign: str,
    astronomy_snapshot: dict[str, Any],
    events: list[dict[str, Any]],
    republish: bool = False,
    preview: bool = False,
) -> tuple[dict[str, Any], bool]:
    if sign not in SIGNS:
        raise ValueError(f'Неизвестный знак: {sign}')
    database.migrate()
    lock_key = f'astra-content-rotation:{sign}'
    now = utc_now()
    try:
      with database.transaction(write=True, lock_key=lock_key) as session:
        previous = session.row(session.execute(
            "SELECT * FROM published_forecasts WHERE forecast_date=? AND sign=? AND status='published' ORDER BY revision DESC LIMIT 1",
            (forecast_date.isoformat(), sign),
        ))
        if previous and not republish and not preview:
            return json.loads(previous['export_json']), False
        revision = int(previous['revision']) + 1 if previous else 1
        if previous and republish:
            session.execute("UPDATE published_forecasts SET status='superseded' WHERE id=?", (previous['id'],))

        context = context_for_sign(events, sign)
        chosen: dict[str, Any] = {}
        diagnostics: dict[str, Any] = {}
        rule_ids = {item['rule_id'] for item in context['rules']}
        topics = set(context['topics'])
        tones = set(context['tones'])

        for block in (*BLOCK_ORDER, 'key_moment', 'event_summary'):
            block_event = _find_event_for_block(events, block)
            if block in {'key_moment', 'event_summary'} and not block_event:
                diagnostics[block] = {'status': 'hidden', 'reason': 'no_calculated_exact_event_with_approved_display_rule'}
                continue
            block_topics = topics | BLOCK_TOPICS.get(block, set())
            selection = select_content(
                session, forecast_date=forecast_date, sign=sign, block_type=block,
                topics=block_topics, rule_ids=rule_ids, tones=tones,
            )
            diagnostics[block] = selection.diagnostics
            if selection.item is None:
                diagnostics[block]['status'] = 'unavailable'
                diagnostics[block]['reason'] = selection.fallback_reason
                if block == 'main':
                    raise RequiredContentMissing(f'Нет одобренного совместимого main-контента для {sign}.')
                continue
            chosen[block] = selection.item
            if selection.fallback_reason:
                diagnostics[block]['status'] = 'fallback'
            if block_event:
                diagnostics[block]['astronomy_event_id'] = block_event.get('id')

        if 'do' in chosen and 'avoid' in chosen and recommendation_conflict(chosen['do'].text, chosen['avoid'].text):
            diagnostics['recommendations'] = {'status': 'incompatible', 'reason': 'direct_action_conflict'}
            chosen.pop('do', None)
            chosen.pop('avoid', None)
            raise RequiredContentMissing('Пара рекомендаций содержит прямое противоречие; публикация остановлена.')

        if previous and republish:
            # Keep prior assignments linked to their immutable publication; the new revision reselects with explicit history.
            pass
        forecast_id = str(uuid.uuid4())
        event_ids = [event['id'] for event in events if event.get('id')]
        items = {block: {'id': item.id, 'version': item.version, 'block_type': item.block_type,
                         'sha256': item.sha256, 'word_count': item.word_count,
                         'allowed_tones': list(item.allowed_tones), 'scope': item.scope}
                 for block, item in chosen.items()}
        metrics = []
        for block, (label, tone) in METRIC_LABELS.items():
            item = chosen.get(block)
            if item:
                metrics.append({'label': label, 'value': 'Текст', 'detail': item.text, 'tone': tone,
                                'editorial_tone': item.allowed_tones[0] if item.allowed_tones else None,
                                'source_content_id': item.id, 'source_content_version': item.version})
        main = chosen['main']
        accent = chosen.get('accent')
        guidance = {key: chosen[key].text if key in chosen else None for key in ('do', 'avoid', 'notice')}
        key_moment = None
        if 'key_moment' in chosen:
            event = _find_event_for_block(events, 'key_moment')
            if event and event.get('exact_time_utc'):
                exact_time = datetime.fromisoformat(event['exact_time_utc'].replace('Z', '+00:00'))
                local_time = exact_time.astimezone(ZoneInfo(TIMEZONE)).strftime('%H:%M')
                key_moment = {'time': local_time, 'time_utc': exact_time.astimezone(timezone.utc).isoformat(), 'description': chosen['key_moment'].text,
                              'source_content_id': chosen['key_moment'].id, 'astronomy_event_id': event['id']}
        event_card = None
        if 'event_summary' in chosen:
            event = _find_event_for_block(events, 'event_summary')
            if event and event.get('site_slug'):
                event_card = {'slug': event['site_slug'], 'title': chosen['event_summary'].text,
                              'start_utc': event.get('start_utc'), 'source_event_id': event['id']}
        publication = {
            'id': forecast_id, 'revision': revision, 'published_at_utc': now,
            'timezone': TIMEZONE, 'algorithm_version': ALGORITHM_VERSION,
            'ruleset_version': context['version'], 'ephemeris_version': astronomy_snapshot.get('ephemeris_version'),
            'content_selections': items,
            'main_target_words': [250, 350], 'main_word_count': main.word_count,
            'main_length_warning': None if 250 <= main.word_count <= 350 else 'seed_main_text_outside_250_350_word_target',
            'fallback_reasons': {block: detail.get('fallback_reason') for block, detail in diagnostics.items()
                                 if isinstance(detail, dict) and detail.get('fallback_reason')},
        }
        export = {
            'source': 'backend', 'forecast_date': forecast_date.isoformat(), 'date': display_date(forecast_date), 'sign': sign,
            'overview': main.text, 'focus': accent.text if accent else None, 'metrics': metrics,
            'keyMoment': key_moment, 'guidance': guidance,
            'eventRelation': None, 'event': event_card,
            'astronomy': {'ephemeris_version': astronomy_snapshot.get('ephemeris_version'),
                          'positions': astronomy_snapshot.get('positions', []),
                          'events': event_ids, 'visualization': astronomy_snapshot.get('visualization')},
            'astrology': context, 'publication': publication,
            'diagnostics': diagnostics,
        }

        session.execute(
            '''INSERT INTO published_forecasts
            (id, forecast_date, sign, revision, status, timezone, created_at, published_at,
             astronomy_snapshot_json, astrology_context_json, event_ids_json, rule_versions_json,
             algorithm_version, fallback_reasons_json, export_json)
            VALUES (?, ?, ?, ?, 'published', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (forecast_id, forecast_date.isoformat(), sign, revision, TIMEZONE, now, now,
             canonical_json(astronomy_snapshot), canonical_json(context), canonical_json(event_ids),
             canonical_json({rule['rule_id']: rule['version'] for rule in context['rules']}),
             ALGORITHM_VERSION, canonical_json(publication['fallback_reasons']), canonical_json(export)),
        )
        for block, item in chosen.items():
            reason = diagnostics.get(block, {}).get('fallback_reason')
            session.execute(
                'INSERT INTO forecast_blocks(forecast_id, block_type, content_id, content_version, fallback_reason) VALUES (?, ?, ?, ?, ?)',
                (forecast_id, block, item.id, item.version, reason),
            )
            insert_assignment(session, forecast_date=forecast_date, sign=sign, block_type=block,
                              item=item, forecast_id=forecast_id, fallback_reason=reason, selected_at=now,
                              revision=revision)
        if preview:
            raise _PreviewResult(export)
        return export, True
    except _PreviewResult as result:
        return result.export, False


def latest_forecasts(database: Database) -> list[dict[str, Any]]:
    database.migrate()
    with database.transaction() as session:
        rows = session.rows(session.execute(
            '''SELECT pf.export_json FROM published_forecasts pf
            JOIN (SELECT sign, MAX(forecast_date) AS latest_date FROM published_forecasts
                  WHERE status='published' GROUP BY sign) latest
            ON latest.sign=pf.sign AND latest.latest_date=pf.forecast_date
            WHERE pf.status='published'
            AND pf.revision=(SELECT MAX(current.revision) FROM published_forecasts current
                             WHERE current.sign=pf.sign AND current.forecast_date=pf.forecast_date AND current.status='published')
            ORDER BY pf.sign'''
        ))
    return [json.loads(row['export_json']) for row in rows]
