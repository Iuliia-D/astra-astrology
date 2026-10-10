from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from .content import canonical_json
from .db import Database, utc_now
from .rules import ASPECTS, aspect_orb, circular_distance, detect_aspects, sign_for_longitude
from .settings import EPHEMERIS_PATH, TIMEZONE

ASTRONOMY_ALGORITHM_VERSION = 'astra-astronomy-astropy-de432s-v1'
BODIES = ('Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto')
SAMPLE_STEP_MINUTES = 60
EXACT_ASPECT_TOLERANCE_DEGREES = 0.001


class AstronomyUnavailable(RuntimeError):
    pass


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _wrap_delta(start: float, end: float) -> float:
    return (end - start + 180.0) % 360.0 - 180.0


def _astropy_position(body: str, instant_utc: datetime) -> tuple[float, float]:
    try:
        from astropy.coordinates import GeocentricTrueEcliptic, get_body, solar_system_ephemeris
        from astropy.time import Time
    except ImportError as exc:
        raise AstronomyUnavailable('Установите зависимости backend из requirements.txt (Astropy).') from exc
    time = Time(instant_utc, scale='utc')
    try:
        coordinate = get_body(body.lower(), time)
        ecliptic = coordinate.transform_to(GeocentricTrueEcliptic(equinox=time))
    except Exception as exc:
        raise AstronomyUnavailable(f'Расчёт {body} для {instant_utc.isoformat()} по локальным эфемеридам не выполнен: {exc}') from exc
    return float(ecliptic.lon.deg) % 360.0, float(ecliptic.lat.deg)


def calculate_day(forecast_date: date, ephemeris_path: Path = EPHEMERIS_PATH) -> dict[str, Any]:
    if not ephemeris_path.is_file():
        raise AstronomyUnavailable(
            f'Не найден локальный JPL DE432s kernel: {ephemeris_path}. '
            'Расчёт и публикация остановлены; backend не подменяет эфемериды фиктивными событиями.'
        )
    try:
        from astropy.coordinates import solar_system_ephemeris
        import astropy
    except ImportError as exc:
        raise AstronomyUnavailable('Установите зависимости backend из requirements.txt (Astropy).') from exc

    local_zone = ZoneInfo(TIMEZONE)
    local_start = datetime.combine(forecast_date, datetime.min.time(), tzinfo=local_zone)
    utc_start = local_start.astimezone(timezone.utc)
    sample_count = 24 * 60 // SAMPLE_STEP_MINUTES
    sample_times = [utc_start + timedelta(minutes=SAMPLE_STEP_MINUTES * i) for i in range(sample_count + 1)]
    eph_sha = file_sha256(ephemeris_path)
    eph_version = f'DE432s:{eph_sha}'
    parameters = {
        'frame': 'geocentric_true_ecliptic', 'zodiac': 'tropical', 'timezone': TIMEZONE,
        'sample_step_minutes': SAMPLE_STEP_MINUTES,
        'exact_aspect_tolerance_degrees': EXACT_ASPECT_TOLERANCE_DEGREES,
        'aspect_orbs_degrees': {key: {'default': value['orb'], 'moon': value['moon_orb']} for key, value in ASPECTS.items()},
        'astropy_version': astropy.__version__, 'kernel_file_sha256': eph_sha,
    }
    try:
        with solar_system_ephemeris.set(str(ephemeris_path)):
            samples: list[dict[str, dict[str, float]]] = []
            for instant in sample_times:
                current: dict[str, dict[str, float]] = {}
                for body in BODIES:
                    longitude, latitude = _astropy_position(body, instant)
                    current[body] = {'longitude': longitude, 'latitude': latitude}
                samples.append(current)
            # Speeds use a centered six-hour finite difference at local noon.
            noon_index = 12
            noon_utc = sample_times[noon_index]
            noon_positions: dict[str, dict[str, Any]] = {}
            for body in BODIES:
                before, after = samples[noon_index - 3][body]['longitude'], samples[noon_index + 3][body]['longitude']
                speed = _wrap_delta(before, after) / 0.25
                longitude = samples[noon_index][body]['longitude']
                noon_positions[body] = {
                    'longitude': round(longitude, 8), 'latitude': round(samples[noon_index][body]['latitude'], 8),
                    'speed_deg_day': round(speed, 8), 'sign': sign_for_longitude(longitude),
                    'degree_in_sign': round(longitude % 30.0, 6), 'retrograde': speed < 0,
                }
            speed_by_body = {body: noon_positions[body]['speed_deg_day'] for body in BODIES}
            events = _aspect_events(sample_times, samples, speed_by_body)
            events.extend(_ingress_events(sample_times, samples))
            for event in events:
                event['id'] = hashlib.sha256(canonical_json({
                    'local_date': forecast_date.isoformat(), 'eph': eph_version, 'event': event,
                }).encode('utf-8')).hexdigest()[:24]
                event['algorithm_version'] = ASTRONOMY_ALGORITHM_VERSION
            events.sort(key=lambda item: (item.get('start_utc') or '', item.get('event_type', ''), item.get('id', '')))
    except AstronomyUnavailable:
        raise
    except Exception as exc:
        raise AstronomyUnavailable(f'Расчёт по указанным эфемеридам не завершён: {exc}') from exc

    return {
        'local_date': forecast_date.isoformat(), 'timezone': TIMEZONE,
        'calculated_at_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'ephemeris_version': eph_version, 'algorithm_version': ASTRONOMY_ALGORITHM_VERSION,
        'parameters': parameters, 'positions': [dict(name=body, **noon_positions[body]) for body in BODIES],
        'events': events,
        'visualization': {
            'coordinate_frame': 'geocentric_true_ecliptic', 'timezone': TIMEZONE,
            'positions': [dict(name=body, longitude=noon_positions[body]['longitude'], latitude=noon_positions[body]['latitude']) for body in BODIES],
        },
    }


def _aspect_deviation(positions: dict[str, dict[str, float]], first: str, second: str, target: float) -> float:
    angle = circular_distance(positions[first]['longitude'], positions[second]['longitude'])
    return abs(angle - target)


def _golden_minimum(function: Any, left: datetime, right: datetime) -> tuple[datetime, float]:
    ratio = (5**0.5 - 1) / 2
    a, b = 0.0, (right - left).total_seconds()
    x1 = b - ratio * (b - a)
    x2 = a + ratio * (b - a)
    f1 = function(left + timedelta(seconds=x1))
    f2 = function(left + timedelta(seconds=x2))
    for _ in range(42):
        if f1 <= f2:
            b, x2, f2 = x2, x1, f1
            x1 = b - ratio * (b - a)
            f1 = function(left + timedelta(seconds=x1))
        else:
            a, x1, f1 = x1, x2, f2
            x2 = a + ratio * (b - a)
            f2 = function(left + timedelta(seconds=x2))
    second = x1 if f1 <= f2 else x2
    instant = left + timedelta(seconds=second)
    return instant, min(f1, f2)


def refine_exact_aspect_time(
    times: list[datetime],
    deviations: list[float],
    deviation_at: Any,
    *,
    tolerance_degrees: float = EXACT_ASPECT_TOLERANCE_DEGREES,
) -> tuple[datetime | None, float]:
    """Refine sampled local minima; only return an exact timestamp inside the explicit angular tolerance."""
    if not times or len(times) != len(deviations):
        raise ValueError('Для уточнения аспекта нужны одинаковые непустые массивы times/deviations.')
    best_index = min(range(len(times)), key=lambda index: deviations[index])
    best_deviation = deviations[best_index]
    best_time: datetime | None = times[best_index] if best_deviation <= tolerance_degrees else None
    for index in range(1, len(times) - 1):
        if not (deviations[index] <= deviations[index - 1] and deviations[index] <= deviations[index + 1]):
            continue
        instant, minimum = _golden_minimum(deviation_at, times[index - 1], times[index + 1])
        if minimum < best_deviation:
            best_time, best_deviation = instant, minimum
    if best_deviation > tolerance_degrees:
        return None, best_deviation
    return best_time, best_deviation


def _aspect_events(times: list[datetime], samples: list[dict[str, dict[str, float]]], speeds: dict[str, float]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for i, first in enumerate(BODIES):
        for second in BODIES[i + 1:]:
            for name, spec in ASPECTS.items():
                orb = aspect_orb(name, (first, second))
                deviations = [_aspect_deviation(sample, first, second, spec['angle']) for sample in samples]
                inside = [index for index, value in enumerate(deviations) if value <= orb]
                if not inside:
                    continue
                local_indices = [index for index in range(1, len(times) - 1)
                                 if deviations[index] <= deviations[index - 1]
                                 and deviations[index] <= deviations[index + 1]
                                 and deviations[index] <= orb]
                best_deviation = min(deviations[index] for index in inside)
                exact = next((times[index] for index in inside if deviations[index] <= EXACT_ASPECT_TOLERANCE_DEGREES), None)
                for index in local_indices:
                    refined_time, refined_deviation = refine_exact_aspect_time(
                        times[index - 1:index + 2], deviations[index - 1:index + 2],
                        lambda at: _aspect_deviation(_positions_at(at, first, second), first, second, spec['angle']),
                    )
                    if refined_deviation < best_deviation:
                        best_deviation = refined_deviation
                    if refined_time is not None and (exact is None or refined_time < exact):
                        exact = refined_time
                midpoint_index = inside[len(inside) // 2]
                midpoint = samples[midpoint_index]
                event = {
                    'event_type': 'aspect', 'aspect': name, 'planets': [first, second],
                    'start_utc': times[min(inside)].isoformat(), 'end_utc': times[max(inside)].isoformat(),
                    'exact_time_utc': exact.isoformat() if exact else None,
                    'exact': exact is not None,
                    'angle': round(circular_distance(midpoint[first]['longitude'], midpoint[second]['longitude']), 6),
                    'orb': round(best_deviation, 6), 'orb_limit': orb,
                    'phase': 'exact' if exact else _phase_for_samples(deviations, inside),
                    'duration_hours': round(max(0, (times[max(inside)] - times[min(inside)]).total_seconds() / 3600), 3),
                    'planet_signs': {first: sign_for_longitude(midpoint[first]['longitude']), second: sign_for_longitude(midpoint[second]['longitude'])},
                    'planet_longitudes': {first: round(midpoint[first]['longitude'], 8), second: round(midpoint[second]['longitude'], 8)},
                    'planet_speeds': {first: speeds[first], second: speeds[second]},
                    'evidence': 'Astropy geocentric true ecliptic longitudes with local DE432s kernel',
                }
                found.append(event)
    return found


def _positions_at(instant: datetime, first: str, second: str) -> dict[str, dict[str, float]]:
    positions = {}
    for body in (first, second):
        longitude, latitude = _astropy_position(body, instant)
        positions[body] = {'longitude': longitude, 'latitude': latitude}
    return positions


def _phase_for_samples(deviations: list[float], inside: list[int]) -> str:
    first, last = min(inside), max(inside)
    before = deviations[first - 1] if first > 0 else float('inf')
    after = deviations[last + 1] if last + 1 < len(deviations) else float('inf')
    if before > after:
        return 'applying'
    if after > before:
        return 'separating'
    return 'within_orb'


def _ingress_events(times: list[datetime], samples: list[dict[str, dict[str, float]]]) -> list[dict[str, Any]]:
    events = []
    for body in BODIES:
        for index in range(len(times) - 1):
            old_sign = sign_for_longitude(samples[index][body]['longitude'])
            new_sign = sign_for_longitude(samples[index + 1][body]['longitude'])
            if old_sign == new_sign:
                continue
            left, right = times[index], times[index + 1]
            left_sign = old_sign
            for _ in range(40):
                mid = left + (right - left) / 2
                longitude, _ = _astropy_position(body, mid)
                if sign_for_longitude(longitude) == left_sign:
                    left = mid
                else:
                    right = mid
            exact = left + (right - left) / 2
            events.append({
                'event_type': 'sign_ingress', 'planet': body, 'from_sign': old_sign, 'to_sign': new_sign,
                'start_utc': exact.isoformat(), 'end_utc': exact.isoformat(),
                'exact_time_utc': exact.isoformat(), 'exact': True,
                'evidence': 'sign boundary crossing calculated from DE432s positions',
            })
    return events


def store_day(database: Database, snapshot: dict[str, Any], *, replace: bool = False) -> None:
    database.migrate()
    eph = snapshot['ephemeris_version']
    algorithm = snapshot['algorithm_version']
    day = snapshot['local_date']
    now = utc_now()
    with database.transaction(write=True, lock_key=f'astra-astronomy:{day}:{eph}:{algorithm}') as session:
        existing = session.row(session.execute(
            'SELECT snapshot_json FROM astronomy_days WHERE local_date=? AND eph_version=? AND algorithm_version=?',
            (day, eph, algorithm),
        ))
        if existing and not replace:
            old_snapshot = json.loads(existing['snapshot_json'])
            # Stable calculations are idempotent despite a changed calculated_at timestamp.
            if _stable_snapshot(old_snapshot) != _stable_snapshot(snapshot):
                raise RuntimeError('Расчёт для этой даты/эфемериды уже отличается; используйте явный --replace.')
            return
        if existing and replace:
            session.execute('DELETE FROM astronomy_day_events WHERE local_date=? AND eph_version=? AND algorithm_version=?', (day, eph, algorithm))
            session.execute('DELETE FROM astronomy_days WHERE local_date=? AND eph_version=? AND algorithm_version=?', (day, eph, algorithm))
        session.execute(
            'INSERT INTO astronomy_days(local_date, timezone, eph_version, algorithm_version, parameters_json, snapshot_json, calculated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (day, snapshot['timezone'], eph, algorithm, canonical_json(snapshot['parameters']), canonical_json(snapshot), snapshot['calculated_at_utc']),
        )
        for event in snapshot['events']:
            data = canonical_json(event)
            calc_hash = hashlib.sha256(data.encode('utf-8')).hexdigest()
            event_id = event['id']
            session.execute(
                '''INSERT INTO astronomical_events
                (id, event_type, start_utc, exact_time, planets_json, data_json, eph_version,
                 calculation_parameters_json, algorithm_version, calculation_hash, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT DO NOTHING''',
                (event_id, event['event_type'], event.get('start_utc') or snapshot['calculated_at_utc'],
                 1 if event.get('exact') else 0, canonical_json(event.get('planets') or [event.get('planet')]),
                 data, eph, canonical_json(snapshot['parameters']), algorithm, calc_hash, now),
            )
            session.execute(
                'INSERT INTO astronomy_day_events(local_date, eph_version, algorithm_version, event_id) VALUES (?, ?, ?, ?) ON CONFLICT DO NOTHING',
                (day, eph, algorithm, event_id),
            )


def _stable_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in snapshot.items() if key != 'calculated_at_utc'}


def load_day(database: Database, forecast_date: date, ephemeris_version: str | None = None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    database.migrate()
    with database.transaction() as session:
        if ephemeris_version:
            row = session.row(session.execute(
                'SELECT * FROM astronomy_days WHERE local_date=? AND eph_version=? ORDER BY algorithm_version DESC LIMIT 1',
                (forecast_date.isoformat(), ephemeris_version),
            ))
        else:
            row = session.row(session.execute(
                'SELECT * FROM astronomy_days WHERE local_date=? ORDER BY calculated_at DESC LIMIT 1',
                (forecast_date.isoformat(),),
            ))
        if not row:
            raise AstronomyUnavailable(f'Для {forecast_date} нет сохранённого расчёта эфемерид; выполните `astra calc --date {forecast_date}`.')
        snapshot = json.loads(row['snapshot_json'])
        events = [json.loads(item['data_json']) for item in session.rows(session.execute(
            '''SELECT ae.data_json FROM astronomical_events ae
            JOIN astronomy_day_events ade ON ade.event_id=ae.id
            WHERE ade.local_date=? AND ade.eph_version=? AND ade.algorithm_version=?
            ORDER BY ae.start_utc, ae.id''',
            (forecast_date.isoformat(), row['eph_version'], row['algorithm_version']),
        ))]
    return snapshot, events
