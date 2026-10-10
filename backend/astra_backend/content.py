from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SIGNS = (
    'aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo',
    'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces',
)
BLOCK_TYPES = {
    'main', 'accent', 'love', 'career', 'energy', 'finance', 'do', 'avoid',
    'notice', 'key_moment', 'event_summary',
}
SCOPES = {'universal', 'contextual', 'specific', 'test_only'}
REVIEW_STATUSES = {'draft', 'approved', 'archived'}
TONES = {'positive', 'neutral', 'cautious', 'tense', 'dynamic', 'reflective'}
RULE_IDS = {f'aspect-{name}' for name in ('conjunction', 'sextile', 'square', 'trine', 'opposition')}
WORD_RE = re.compile(r"[\w]+(?:['’\-][\w]+)*", re.UNICODE)


@dataclass(frozen=True)
class ContentItem:
    id: str
    version: int
    block_type: str
    text: str
    scope: str
    topics: tuple[str, ...]
    allowed_signs: tuple[str, ...]
    required_rule_ids: tuple[str, ...]
    forbidden_rule_ids: tuple[str, ...]
    allowed_tones: tuple[str, ...]
    min_gap_days: int
    review_status: str
    notes: str | None
    word_count: int
    sha256: str
    raw: dict[str, Any]


class SeedValidationError(ValueError):
    pass


def word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def load_seed(path: Path) -> tuple[dict[str, Any], list[ContentItem]]:
    try:
        document = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as exc:
        raise SeedValidationError(f'Не удалось прочитать seed JSON {path}: {exc}') from exc
    if not isinstance(document, dict) or document.get('project') != 'ASTRA':
        raise SeedValidationError('Ожидается JSON-объект с project="ASTRA".')
    if document.get('schema_version') != '1.0.0' or document.get('locale') != 'ru-RU':
        raise SeedValidationError('Неподдерживаемые schema_version или locale seed-файла.')
    if document.get('timezone') != 'Europe/Moscow':
        raise SeedValidationError('Для seed v1 ожидается timezone Europe/Moscow.')
    if set(document.get('signs', [])) != set(SIGNS):
        raise SeedValidationError('Seed должен содержать ровно 12 известных знаков.')
    entries = document.get('content_items')
    if not isinstance(entries, list):
        raise SeedValidationError('content_items должен быть массивом.')
    items: list[ContentItem] = []
    seen: set[tuple[str, int]] = set()
    for index, row in enumerate(entries):
        prefix = f'content_items[{index}]'
        if not isinstance(row, dict):
            raise SeedValidationError(f'{prefix}: ожидался объект.')
        required = ('id', 'version', 'block_type', 'text', 'scope', 'topics', 'allowed_signs', 'required_rule_ids', 'forbidden_rule_ids', 'allowed_tones', 'min_gap_days', 'review_status')
        missing = [field for field in required if field not in row]
        if missing:
            raise SeedValidationError(f'{prefix}: отсутствуют поля {", ".join(missing)}.')
        key = (row['id'], row['version'])
        if not isinstance(key[0], str) or not key[0] or not isinstance(key[1], int) or key[1] < 1:
            raise SeedValidationError(f'{prefix}: некорректные id/version.')
        if key in seen:
            raise SeedValidationError(f'{prefix}: повторяется id/version {key}.')
        seen.add(key)
        if row['block_type'] not in BLOCK_TYPES or row['scope'] not in SCOPES or row['review_status'] not in REVIEW_STATUSES:
            raise SeedValidationError(f'{prefix}: неизвестный block_type, scope или review_status.')
        if not isinstance(row['text'], str) or not row['text'].strip():
            raise SeedValidationError(f'{prefix}: text должен быть непустой строкой.')
        for field in ('topics', 'allowed_signs', 'required_rule_ids', 'forbidden_rule_ids', 'allowed_tones'):
            if not isinstance(row[field], list) or not all(isinstance(value, str) for value in row[field]):
                raise SeedValidationError(f'{prefix}: {field} должен быть массивом строк.')
        unknown_signs = set(row['allowed_signs']) - set(SIGNS)
        unknown_tones = set(row['allowed_tones']) - TONES
        unknown_rules = (set(row['required_rule_ids']) | set(row['forbidden_rule_ids'])) - RULE_IDS
        if unknown_signs or unknown_tones or unknown_rules:
            raise SeedValidationError(f'{prefix}: неизвестные signs={sorted(unknown_signs)}, tones={sorted(unknown_tones)}, rules={sorted(unknown_rules)}.')
        if not isinstance(row['min_gap_days'], int) or row['min_gap_days'] < 0:
            raise SeedValidationError(f'{prefix}: min_gap_days должен быть неотрицательным целым числом.')
        count = word_count(row['text'])
        normalized = canonical_json(row)
        items.append(ContentItem(
            id=row['id'], version=row['version'], block_type=row['block_type'], text=row['text'],
            scope=row['scope'], topics=tuple(row['topics']), allowed_signs=tuple(row['allowed_signs']),
            required_rule_ids=tuple(row['required_rule_ids']), forbidden_rule_ids=tuple(row['forbidden_rule_ids']),
            allowed_tones=tuple(row['allowed_tones']), min_gap_days=row['min_gap_days'],
            review_status=row['review_status'], notes=row.get('notes'), word_count=count,
            sha256=hashlib.sha256(normalized.encode('utf-8')).hexdigest(), raw=row,
        ))
    return document, items


def compatibility_counts(items: list[ContentItem]) -> dict[str, dict[str, int]]:
    return {
        block: {
            sign: sum(
                item.block_type == block and sign in item.allowed_signs
                and item.review_status == 'approved' and item.scope != 'test_only'
                for item in items
            )
            for sign in SIGNS
        }
        for block in sorted(BLOCK_TYPES)
    }


def seed_summary(items: list[ContentItem]) -> dict[str, Any]:
    counts = Counter(item.block_type for item in items)
    mains = [item.word_count for item in items if item.block_type == 'main']
    return {
        'item_count': len(items),
        'approved_count': sum(item.review_status == 'approved' for item in items),
        'test_only_count': sum(item.scope == 'test_only' for item in items),
        'block_type_counts': dict(sorted(counts.items())),
        'main_word_counts': {item.id: item.word_count for item in items if item.block_type == 'main'},
        'main_target_words': [250, 350],
        'main_outside_target_count': sum(not 250 <= value <= 350 for value in mains),
        'compatible_approved_public_pool_by_block_sign': compatibility_counts(items),
    }
