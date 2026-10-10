from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .content import SIGNS

RULES_VERSION = 1
RULESET_VERSION = 'astra-astrology-rules-v1'
SIGNIFICANCE_MODEL_VERSION = 'astra-significance-v1'

PLANET_THEMES: dict[str, tuple[str, ...]] = {
    'Sun': ('identity', 'goals', 'priorities'),
    'Moon': ('emotions', 'habits', 'daily_needs'),
    'Mercury': ('communication', 'information', 'learning', 'decisions'),
    'Venus': ('relationships', 'values', 'comfort', 'attraction'),
    'Mars': ('action', 'initiative', 'competition', 'conflict'),
    'Jupiter': ('growth', 'opportunities', 'learning', 'expansion'),
    'Saturn': ('responsibility', 'limits', 'discipline', 'long_term_tasks'),
    'Uranus': ('change', 'independence', 'experimentation'),
    'Neptune': ('imagination', 'ideals', 'uncertainty', 'misunderstanding'),
    'Pluto': ('control', 'power', 'shared_resources', 'transformation'),
}

HOUSE_THEMES: tuple[tuple[str, ...], ...] = (
    ('self_definition', 'personal_priorities'),
    ('money', 'personal_resources', 'values'),
    ('communication', 'learning', 'short_travel'),
    ('home', 'family', 'private_space'),
    ('romance', 'creativity', 'hobbies'),
    ('work', 'routine', 'daily_duties'),
    ('partnerships', 'agreements', 'relationships'),
    ('shared_finances', 'obligations', 'shared_resources'),
    ('learning', 'worldview', 'long_travel'),
    ('career', 'public_role', 'long_term_goals'),
    ('friends', 'communities', 'collective_plans'),
    ('solitude', 'completion', 'reflection'),
)

ASPECTS: dict[str, dict[str, Any]] = {
    'conjunction': {'angle': 0.0, 'orb': 6.0, 'moon_orb': 3.0, 'frame': 'совместное усиление или смешение тематик'},
    'sextile': {'angle': 60.0, 'orb': 3.0, 'moon_orb': 2.0, 'frame': 'возможность взаимодействия, требующая участия'},
    'square': {'angle': 90.0, 'orb': 5.0, 'moon_orb': 2.0, 'frame': 'напряжение или необходимость корректировки'},
    'trine': {'angle': 120.0, 'orb': 5.0, 'moon_orb': 2.0, 'frame': 'более согласованное взаимодействие'},
    'opposition': {'angle': 180.0, 'orb': 6.0, 'moon_orb': 3.0, 'frame': 'противостояние стремлений или необходимость баланса'},
}

ASPECT_WEIGHT = {'conjunction': 1.0, 'opposition': 0.9, 'square': 0.85, 'trine': 0.7, 'sextile': 0.6}
PLANET_WEIGHT = {'Sun': 1.0, 'Moon': 1.0, 'Mercury': 0.85, 'Venus': 0.85, 'Mars': 0.85, 'Jupiter': 0.7, 'Saturn': 0.7, 'Uranus': 0.55, 'Neptune': 0.55, 'Pluto': 0.55}


@dataclass(frozen=True)
class Interpretation:
    rule_id: str
    rule_version: int
    topics: tuple[str, ...]
    tone: str
    priority: float
    explanation: str
    permitted_block_types: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


RULES: dict[str, dict[str, Any]] = {
    f'aspect-{name}': {
        'rule_id': f'aspect-{name}',
        'version': RULES_VERSION,
        'condition': {'event_type': 'aspect', 'aspect': name},
        'planet_topics': 'union of the documented planet-theme dictionary',
        'house_topics': 'whole-sign house themes for each participating planet',
        'tone': 'neutral',
        'priority': ASPECT_WEIGHT[name],
        'validity': 'calculated aspect interval only',
        'permitted_block_types': ['accent', 'love', 'career', 'energy', 'finance', 'do', 'avoid', 'notice'],
        'hard_constraints': ['event must have a calculated aspect and source positions'],
        'soft_preferences': ['topic overlap', 'tone match'],
        'exceptions': [],
        'explanation_template': ASPECTS[name]['frame'],
    }
    for name in ASPECTS
}


def circular_distance(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0)


def zodiac_index(longitude: float) -> int:
    return int((longitude % 360.0) // 30.0)


def sign_for_longitude(longitude: float) -> str:
    return SIGNS[zodiac_index(longitude)]


def whole_sign_house(user_sign: str, planet_sign: str) -> int:
    return (SIGNS.index(planet_sign) - SIGNS.index(user_sign)) % 12 + 1


def aspect_orb(aspect: str, planets: tuple[str, str]) -> float:
    item = ASPECTS[aspect]
    return item['moon_orb'] if 'Moon' in planets else item['orb']


def detect_aspects(positions: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    planets = list(positions)
    found: list[dict[str, Any]] = []
    for i, first in enumerate(planets):
        for second in planets[i + 1:]:
            angle = circular_distance(float(positions[first]['longitude']), float(positions[second]['longitude']))
            for name, spec in ASPECTS.items():
                orb = aspect_orb(name, (first, second))
                deviation = abs(angle - spec['angle'])
                if deviation > orb:
                    continue
                speed_a = float(positions[first].get('speed_deg_day', 0.0))
                speed_b = float(positions[second].get('speed_deg_day', 0.0))
                next_angle = circular_distance(
                    float(positions[first]['longitude']) + speed_a / 24.0,
                    float(positions[second]['longitude']) + speed_b / 24.0,
                )
                phase = 'exact' if deviation <= 1e-3 else ('applying' if abs(next_angle - spec['angle']) < deviation else 'separating')
                found.append({
                    'event_type': 'aspect', 'aspect': name, 'planets': [first, second],
                    'angle': round(angle, 6), 'orb': round(deviation, 6), 'orb_limit': orb,
                    'phase': phase, 'exact_time_utc': None,
                    'planet_signs': {first: positions[first]['sign'], second: positions[second]['sign']},
                    'planet_longitudes': {first: positions[first]['longitude'], second: positions[second]['longitude']},
                    'planet_speeds': {first: speed_a, second: speed_b},
                })
    return found


def significance(event: dict[str, Any]) -> float:
    """Deterministic internal ordering weight. It is not a scientific or outcome score."""
    aspect = event.get('aspect')
    if aspect not in ASPECTS:
        return 0.0
    planets = event.get('planets', [])
    limit = float(event.get('orb_limit', aspect_orb(aspect, tuple(planets))))
    closeness = max(0.0, 1.0 - float(event.get('orb', limit)) / limit) if limit else 0.0
    body = sum(PLANET_WEIGHT.get(p, 0.5) for p in planets) / max(1, len(planets))
    speeds = event.get('planet_speeds', {}).values()
    speed = sum(abs(float(v)) for v in speeds) / max(1, len(event.get('planet_speeds', {})))
    motion_weight = 1.0 / (1.0 + speed)
    duration_hours = min(24.0, max(0.0, float(event.get('duration_hours', 0.0))))
    duration_weight = 0.75 + min(duration_hours / 24.0, 1.0) * 0.25
    phase_weight = 1.0 if event.get('phase') == 'exact' else 0.9 if event.get('phase') == 'applying' else 0.8
    return round(ASPECT_WEIGHT[aspect] * body * (0.7 + 0.3 * closeness) * motion_weight * duration_weight * phase_weight, 6)


def interpret_event(event: dict[str, Any], user_sign: str) -> Interpretation | None:
    if event.get('event_type') != 'aspect' or event.get('aspect') not in ASPECTS:
        return None
    rule_id = f"aspect-{event['aspect']}"
    planets = event.get('planets', [])
    signs = event.get('planet_signs', {})
    if len(planets) != 2 or any(p not in PLANET_THEMES or signs.get(p) not in SIGNS for p in planets):
        return None
    longitudes = event.get('planet_longitudes', {})
    if any(not isinstance(longitudes.get(planet), (int, float)) for planet in planets):
        return None
    calculated_angle = circular_distance(float(longitudes[planets[0]]), float(longitudes[planets[1]]))
    if abs(calculated_angle - ASPECTS[event['aspect']]['angle']) > aspect_orb(event['aspect'], tuple(planets)):
        return None
    topics: set[str] = set()
    for planet in planets:
        topics.update(PLANET_THEMES[planet])
        house = whole_sign_house(user_sign, signs[planet])
        topics.update(HOUSE_THEMES[house - 1])
    frame = ASPECTS[event['aspect']]['frame']
    tone = 'neutral'  # The approved rule set has no rule that derives a non-neutral tone from planet pairings.
    priority = significance(event)
    return Interpretation(
        rule_id=rule_id,
        rule_version=RULES_VERSION,
        topics=tuple(sorted(topics)),
        tone=tone,
        priority=priority,
        explanation=f"{planets[0]} и {planets[1]}: {frame}; солнечные дома рассчитаны по знаку {user_sign}.",
        permitted_block_types=tuple(RULES[rule_id]['permitted_block_types']),
    )


def context_for_sign(events: list[dict[str, Any]], sign: str) -> dict[str, Any]:
    interpreted = []
    for event in events:
        rule = interpret_event(event, sign)
        if rule is not None:
            interpreted.append({**event, 'significance_weight': significance(event), 'interpretation': rule.as_dict()})
    interpreted.sort(key=lambda item: (-item['significance_weight'], item.get('start_utc', '')))
    return {
        'version': RULESET_VERSION,
        'sign': sign,
        'neutral': not interpreted,
        'topics': sorted({topic for event in interpreted for topic in event['interpretation']['topics']}),
        'tones': sorted({event['interpretation']['tone'] for event in interpreted}) or ['neutral'],
        'rules': [{'rule_id': event['interpretation']['rule_id'], 'version': RULES_VERSION, 'reason': event['interpretation']['explanation']} for event in interpreted],
        'events': interpreted,
    }
