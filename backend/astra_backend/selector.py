from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from typing import Any

from .content import ContentItem
from .db import Session


@dataclass(frozen=True)
class Selection:
    item: ContentItem | None
    fallback_reason: str | None
    diagnostics: dict[str, Any]


def _from_row(row: dict[str, Any]) -> ContentItem:
    raw = json.loads(row['raw_json'])
    return ContentItem(
        id=row['id'], version=row['version'], block_type=row['block_type'], text=row['text'],
        scope=row['scope'], topics=tuple(json.loads(row['topics_json'])),
        allowed_signs=tuple(json.loads(row['allowed_signs_json'])),
        required_rule_ids=tuple(json.loads(row['required_rule_ids_json'])),
        forbidden_rule_ids=tuple(json.loads(row['forbidden_rule_ids_json'])),
        allowed_tones=tuple(json.loads(row['allowed_tones_json'])),
        min_gap_days=row['min_gap_days'], review_status=row['review_status'], notes=row['notes'],
        word_count=row['word_count'], sha256=row['sha256'], raw=raw,
    )


def compatible(item: ContentItem, *, sign: str, topics: set[str], rule_ids: set[str]) -> bool:
    if item.review_status != 'approved' or item.scope == 'test_only' or sign not in item.allowed_signs:
        return False
    if set(item.required_rule_ids) - rule_ids or set(item.forbidden_rule_ids) & rule_ids:
        return False
    if item.scope in {'contextual', 'specific'} and not (set(item.topics) & topics):
        return False
    if item.scope == 'specific' and not (set(item.required_rule_ids) & rule_ids):
        return False
    return True


def select_content(
    session: Session,
    *,
    forecast_date: date,
    sign: str,
    block_type: str,
    topics: set[str],
    rule_ids: set[str],
    tones: set[str],
) -> Selection:
    rows = session.rows(session.execute(
        "SELECT * FROM content_items WHERE block_type=? AND review_status='approved' ORDER BY id, version",
        (block_type,),
    ))
    pool = [_from_row(row) for row in rows]
    allowed = [item for item in pool if compatible(item, sign=sign, topics=topics, rule_ids=rule_ids)]
    if not allowed:
        rejected = []
        for item in pool:
            reasons = []
            if item.review_status != 'approved': reasons.append('review_status_not_approved')
            if item.scope == 'test_only': reasons.append('test_only_scope_forbidden')
            if sign not in item.allowed_signs: reasons.append('sign_not_allowed')
            if set(item.required_rule_ids) - rule_ids: reasons.append('required_rule_missing')
            if set(item.forbidden_rule_ids) & rule_ids: reasons.append('forbidden_rule_active')
            if item.scope in {'contextual', 'specific'} and not (set(item.topics) & topics): reasons.append('contextual_topic_missing')
            if item.scope == 'specific' and not (set(item.required_rule_ids) & rule_ids): reasons.append('specific_content_has_no_matching_rule')
            rejected.append({'id': item.id, 'version': item.version, 'reasons': reasons})
        return Selection(None, 'no_hard_compatible_approved_content', {'candidate_count': 0, 'rejected_items': rejected})

    topic_match = lambda item: not topics or not item.topics or bool(set(item.topics) & topics)
    tone_match = lambda item: not tones or not item.allowed_tones or bool(set(item.allowed_tones) & tones)
    full = [item for item in allowed if topic_match(item) and tone_match(item)]
    topic_soft = [item for item in allowed if tone_match(item)]
    tone_soft = [item for item in allowed if topic_match(item)]
    tiers: list[tuple[list[ContentItem], str | None]] = [
        (full, None), (topic_soft, 'soft_topic_preference_relaxed'),
        (tone_soft, 'soft_tone_preference_relaxed'),
        (allowed, 'soft_topic_and_tone_preferences_relaxed'),
    ]

    history_rows = session.rows(session.execute(
        '''SELECT content_id, content_version,
        MAX(CASE WHEN forecast_date<? THEN forecast_date END) AS last_date,
        MIN(CASE WHEN forecast_date>? THEN forecast_date END) AS next_date,
        COUNT(*) AS uses
        FROM content_assignments WHERE sign=? AND block_type=? AND forecast_date<>?
        GROUP BY content_id, content_version''',
        (forecast_date.isoformat(), forecast_date.isoformat(), sign, block_type, forecast_date.isoformat()),
    ))
    last_used = {(row['content_id'], row['content_version']): date.fromisoformat(row['last_date']) for row in history_rows if row['last_date']}
    next_used = {(row['content_id'], row['content_version']): date.fromisoformat(row['next_date']) for row in history_rows if row['next_date']}
    item_by_key = {(item.id, item.version): item for item in allowed}
    history = [row for row in history_rows if (row['content_id'], row['content_version']) in item_by_key]
    eligible = []
    for item in allowed:
        last = last_used.get((item.id, item.version))
        following = next_used.get((item.id, item.version))
        far_enough_before = last is None or (forecast_date - last).days >= item.min_gap_days
        far_enough_after = following is None or (following - forecast_date).days >= item.min_gap_days
        if far_enough_before and far_enough_after:
            eligible.append(item)

    selected_pool: list[ContentItem] = []
    soft_reason: str | None = None
    used_tier: list[ContentItem] = []
    for candidates, reason in tiers:
        used_tier = candidates
        selected_pool = [item for item in candidates if item in eligible]
        if selected_pool:
            soft_reason = reason
            break

    rotation_fallback = False
    if not selected_pool:
        # All compatible candidates are inside their minimum-gap windows: reuse the least recently used.
        selected_pool = used_tier or allowed
        rotation_fallback = True
        soft_reason = soft_reason or tiers[-1][1]

    selected_pool.sort(key=lambda item: (
        -len(set(item.topics) & topics),
        last_used.get((item.id, item.version), date.min), item.id, item.version,
    ))
    chosen = selected_pool[0]
    reasons = [reason for reason in (soft_reason, 'compatible_pool_exhausted_min_gap' if rotation_fallback else None) if reason]
    fallback = '+'.join(reasons) or None
    history_count = len(history)
    diagnostic = {
        'candidate_count': len(allowed),
        'fresh_candidate_count': len(eligible),
        'full_match_candidate_count': len(full),
        'history_assignment_count': history_count,
        'rotation_pool_exhausted': rotation_fallback,
        'selected_id': chosen.id,
        'selected_version': chosen.version,
        'selected_scope': chosen.scope,
        'selected_tone': chosen.allowed_tones[0] if chosen.allowed_tones else None,
        'topic_overlap': sorted(set(chosen.topics) & topics),
        'fallback_reason': fallback,
        'compatible_candidate_ids': [item.id for item in allowed],
        'full_match_candidate_ids': [item.id for item in full],
        'fallback_tier_candidate_ids': [item.id for item in used_tier],
        'rejected_items': [
            {'id': item.id, 'version': item.version, 'reasons': _rejection_reasons(item, sign, topics, rule_ids)}
            for item in pool if not compatible(item, sign=sign, topics=topics, rule_ids=rule_ids)
        ],
    }
    return Selection(chosen, fallback, diagnostic)


def _rejection_reasons(item: ContentItem, sign: str, topics: set[str], rule_ids: set[str]) -> list[str]:
    reasons = []
    if item.review_status != 'approved': reasons.append('review_status_not_approved')
    if item.scope == 'test_only': reasons.append('test_only_scope_forbidden')
    if sign not in item.allowed_signs: reasons.append('sign_not_allowed')
    if set(item.required_rule_ids) - rule_ids: reasons.append('required_rule_missing')
    if set(item.forbidden_rule_ids) & rule_ids: reasons.append('forbidden_rule_active')
    if item.scope in {'contextual', 'specific'} and not (set(item.topics) & topics): reasons.append('contextual_topic_missing')
    if item.scope == 'specific' and not (set(item.required_rule_ids) & rule_ids): reasons.append('specific_content_has_no_matching_rule')
    return reasons


def insert_assignment(session: Session, *, forecast_date: date, sign: str, block_type: str,
                      item: ContentItem, forecast_id: str, fallback_reason: str | None,
                      selected_at: str, revision: int) -> None:
    session.execute(
        '''INSERT INTO content_assignments
        (forecast_date, sign, block_type, revision, content_id, content_version, forecast_id, selected_at, fallback_reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (forecast_date.isoformat(), sign, block_type, revision, item.id, item.version, forecast_id, selected_at, fallback_reason),
    )


def recommendation_conflict(do_text: str, avoid_text: str) -> bool:
    """Detect only direct quoted-action contradictions; do not infer lexical semantics."""
    do = ' '.join(do_text.casefold().split())
    avoid = ' '.join(avoid_text.casefold().split())
    if avoid.startswith('не '):
        prohibited_action = avoid[3:].strip(' .,!?:;')
        if prohibited_action and prohibited_action in do:
            return True
    if do.startswith('не '):
        prohibited_action = do[3:].strip(' .,!?:;')
        if prohibited_action and prohibited_action in avoid:
            return True
    return False
