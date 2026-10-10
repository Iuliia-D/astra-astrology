from __future__ import annotations

import json
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from astra_backend.astronomy import AstronomyUnavailable, _golden_minimum, calculate_day, refine_exact_aspect_time
from astra_backend.content import SIGNS, SeedValidationError, load_seed
from astra_backend.db import Database
from astra_backend.export import write_export
from astra_backend.forecast import build_forecast
from astra_backend.rules import (
    ASPECTS, HOUSE_THEMES, PLANET_THEMES, aspect_orb, circular_distance,
    context_for_sign, detect_aspects, interpret_event, sign_for_longitude, whole_sign_house,
)
from astra_backend.seed import SeedConflictError, import_seed
from astra_backend.settings import EPHEMERIS_PATH, SEED_PATH
from astra_backend.verify import verify_database


class BackendTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix='astra-backend-')
        self.db_path = Path(self.temp.name) / 'astra.sqlite3'
        self.db = Database(f'sqlite:///{self.db_path}')
        self.seed_result = import_seed(self.db)
        self.snapshot = {
            'local_date': '2026-10-10', 'timezone': 'Europe/Moscow',
            'ephemeris_version': 'TEST-FIXTURE-ONLY', 'algorithm_version': 'test-fixture',
            'parameters': {'fixture': True}, 'calculated_at_utc': '2026-10-09T21:00:00+00:00',
            'positions': [], 'events': [], 'visualization': None,
        }

    def tearDown(self) -> None:
        self.temp.cleanup()

    def publish(self, target: date, sign: str = 'aries', *, republish: bool = False):
        return build_forecast(self.db, forecast_date=target, sign=sign,
                              astronomy_snapshot=self.snapshot, events=[], republish=republish)


class ContentImportTests(BackendTestCase):
    def test_seed_import_is_lossless_idempotent_and_reports_real_pools(self) -> None:
        self.assertEqual(self.seed_result['inserted'], 53)
        self.assertEqual(self.seed_result['test_only_count'], 2)
        report = import_seed(self.db)
        self.assertEqual((report['inserted'], report['unchanged']), (0, 53))
        self.assertEqual(report['main_word_counts'], {
            'main-universal-001': 165, 'main-universal-002': 163, 'main-universal-003': 161,
        })
        counts = report['compatible_approved_public_pool_by_block_sign']
        self.assertEqual(counts['main']['aries'], 3)
        self.assertEqual(counts['love']['aries'], 6)
        self.assertEqual(counts['key_moment']['aries'], 0)
        self.assertEqual(counts['event_summary']['aries'], 0)
        with self.db.transaction() as session:
            row = session.row(session.execute("SELECT raw_json FROM content_items WHERE id='main-universal-001' AND version=1"))
        source = json.loads(SEED_PATH.read_text(encoding='utf-8'))['content_items'][0]
        self.assertEqual(json.loads(row['raw_json']), source)

    def test_same_version_changes_are_rejected_without_overwriting(self) -> None:
        source = json.loads(SEED_PATH.read_text(encoding='utf-8'))
        source['content_items'][0]['text'] += ' изменено'
        modified = Path(self.temp.name) / 'modified.json'
        modified.write_text(json.dumps(source, ensure_ascii=False), encoding='utf-8')
        with self.assertRaises(SeedConflictError):
            import_seed(self.db, modified)
        with self.db.transaction() as session:
            row = session.row(session.execute("SELECT text FROM content_items WHERE id='main-universal-001' AND version=1"))
        self.assertNotIn('изменено', row['text'])

    def test_metadata_validation_fails_closed(self) -> None:
        source = json.loads(SEED_PATH.read_text(encoding='utf-8'))
        source['content_items'][0]['allowed_tones'] = ['invented-tone']
        bad = Path(self.temp.name) / 'bad.json'
        bad.write_text(json.dumps(source, ensure_ascii=False), encoding='utf-8')
        with self.assertRaises(SeedValidationError):
            load_seed(bad)

    def test_database_audit_detects_mutated_seed_rows(self) -> None:
        with self.db.transaction(write=True) as session:
            session.execute(
                "UPDATE content_items SET raw_json=? WHERE id='main-universal-001' AND version=1",
                (json.dumps({'id': 'main-universal-001', 'version': 1}, ensure_ascii=False),),
            )
        with self.assertRaisesRegex(RuntimeError, 'отличается от утверждённого источника'):
            verify_database(self.db)


class AstronomyAndRulesTests(unittest.TestCase):
    def test_whole_sign_houses_for_all_twelve_signs(self) -> None:
        for index, sign in enumerate(SIGNS):
            self.assertEqual(whole_sign_house(sign, sign), 1)
            self.assertEqual(whole_sign_house(sign, SIGNS[(index + 1) % 12]), 2)
            self.assertEqual(whole_sign_house(sign, SIGNS[(index + 11) % 12]), 12)
        for sign in SIGNS:
            self.assertEqual(len(HOUSE_THEMES), 12)

    def test_planet_themes_aspect_orbs_and_zero_crossing(self) -> None:
        self.assertEqual(PLANET_THEMES['Mercury'], ('communication', 'information', 'learning', 'decisions'))
        self.assertEqual(circular_distance(359.0, 1.0), 2.0)
        self.assertEqual(sign_for_longitude(360.0), 'aries')
        self.assertEqual(sign_for_longitude(-0.1), 'pisces')
        self.assertEqual(aspect_orb('conjunction', ('Moon', 'Mars')), 3.0)
        self.assertEqual(aspect_orb('sextile', ('Moon', 'Venus')), 2.0)
        self.assertEqual(aspect_orb('conjunction', ('Sun', 'Mars')), 6.0)
        self.assertEqual(aspect_orb('square', ('Venus', 'Mars')), 5.0)
        for aspect in ('conjunction', 'sextile', 'square', 'trine', 'opposition'):
            self.assertIn(aspect, ASPECTS)

    def test_aspect_detection_phase_and_interpretation_require_calculated_evidence(self) -> None:
        positions = {
            'Moon': {'longitude': 359.8, 'sign': 'pisces', 'speed_deg_day': 13.0},
            'Mercury': {'longitude': 0.4, 'sign': 'aries', 'speed_deg_day': 1.0},
        }
        found = detect_aspects(positions)
        conjunction = next(item for item in found if item['aspect'] == 'conjunction')
        self.assertAlmostEqual(conjunction['orb'], 0.6)
        self.assertIn(conjunction['phase'], {'applying', 'separating'})
        interpretation = interpret_event(conjunction, 'aries')
        self.assertIsNotNone(interpretation)
        self.assertEqual(interpretation.rule_id, 'aspect-conjunction')
        self.assertEqual(interpretation.tone, 'neutral')
        self.assertIsNone(interpret_event({'event_type': 'ingress', 'planet': 'Mercury'}, 'aries'))
        self.assertIsNone(interpret_event({'event_type': 'aspect', 'aspect': 'unknown', 'planets': ['Moon', 'Mars']}, 'aries'))
        empty_context = context_for_sign([{'event_type': 'ingress', 'planet': 'Mercury'}], 'aries')
        self.assertTrue(empty_context['neutral'])
        self.assertEqual(empty_context['rules'], [])

    def test_numeric_search_finds_an_exact_time_without_network(self) -> None:
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        exact = start + timedelta(minutes=30)
        times = [start, start + timedelta(hours=1), start + timedelta(hours=2)]
        def deviation(at: datetime) -> float:
            moving_longitude = 359.0 + 2.0 * (at - start).total_seconds() / 3600
            return circular_distance(moving_longitude, 0.0)
        result, error = refine_exact_aspect_time(times, [3.0, 1.0, 3.0], deviation)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertLess(abs((result - exact).total_seconds()), 0.01)
        self.assertLess(error, 0.01)

    def test_missing_local_jpl_file_never_falls_back_to_fake_data(self) -> None:
        with self.assertRaises(AstronomyUnavailable):
            calculate_day(date(2026, 10, 10), Path(self._temp_nonexistent_path()))

    @unittest.skipUnless(EPHEMERIS_PATH.is_file(), 'локальный DE432s не установлен')
    def test_local_de432s_reproduces_march_2026_solar_ingress(self) -> None:
        snapshot = calculate_day(date(2026, 3, 20), EPHEMERIS_PATH)
        sun = next(body for body in snapshot['positions'] if body['name'] == 'Sun')
        self.assertLess(circular_distance(sun['longitude'], 0.0), 0.4)
        self.assertEqual(len(snapshot['positions']), 10)
        ingress = next(event for event in snapshot['events']
                       if event['event_type'] == 'sign_ingress' and event['planet'] == 'Sun'
                       and event['from_sign'] == 'pisces' and event['to_sign'] == 'aries')
        exact = datetime.fromisoformat(ingress['exact_time_utc'])
        expected = datetime(2026, 3, 20, 14, 45, tzinfo=timezone.utc)
        self.assertLess(abs((exact - expected).total_seconds()), 15 * 60)

    def _temp_nonexistent_path(self) -> str:
        return str(Path(tempfile.gettempdir()) / 'astra-jpl-kernel-deliberately-absent.bsp')


class PublicationTests(BackendTestCase):
    def test_approved_content_build_export_and_no_test_only_publication(self) -> None:
        forecast, created = self.publish(date(2026, 10, 10))
        self.assertTrue(created)
        self.assertEqual(forecast['source'], 'backend')
        self.assertIn('Сегодня полезно начать', forecast['overview'])
        self.assertEqual(len(forecast['metrics']), 4)
        self.assertIsNone(forecast['keyMoment'])
        self.assertIsNone(forecast['event'])
        self.assertIsNone(forecast['eventRelation'])
        self.assertEqual(forecast['astrology']['rules'], [])
        self.assertEqual(forecast['publication']['main_length_warning'], 'seed_main_text_outside_250_350_word_target')
        self.assertEqual(forecast['diagnostics']['key_moment']['reason'], 'no_calculated_exact_event_with_approved_display_rule')
        with self.db.transaction() as session:
            scopes = session.rows(session.execute(
                '''SELECT ci.scope FROM forecast_blocks fb JOIN content_items ci
                ON ci.id=fb.content_id AND ci.version=fb.content_version'''
            ))
        self.assertTrue(scopes)
        self.assertNotIn('test_only', [row['scope'] for row in scopes])

    def test_retry_is_immutable_and_republication_keeps_prior_revision(self) -> None:
        first, created = self.publish(date(2026, 10, 10))
        self.assertTrue(created)
        second, created_again = self.publish(date(2026, 10, 10))
        self.assertFalse(created_again)
        self.assertEqual(first, second)
        replacement, republished = self.publish(date(2026, 10, 10), republish=True)
        self.assertTrue(republished)
        self.assertEqual(replacement['publication']['revision'], 2)
        with self.db.transaction() as session:
            rows = session.rows(session.execute('SELECT revision, status, export_json FROM published_forecasts ORDER BY revision'))
        self.assertEqual([(row['revision'], row['status']) for row in rows], [(1, 'superseded'), (2, 'published')])
        self.assertEqual(json.loads(rows[0]['export_json']), first)

    def test_no_repeat_before_pool_exhaustion_and_fallback_is_recorded(self) -> None:
        first_three = []
        for day in range(10, 13):
            forecast, _ = self.publish(date(2026, 10, day))
            first_three.append(forecast['publication']['content_selections']['main']['id'])
        self.assertEqual(len(set(first_three)), 3)
        fourth, _ = self.publish(date(2026, 10, 13))
        self.assertEqual(fourth['publication']['content_selections']['main']['id'], first_three[0])
        self.assertIn('compatible_pool_exhausted_min_gap', fourth['publication']['fallback_reasons']['main'])

    def test_missing_optional_block_is_omitted_without_fabricated_replacement(self) -> None:
        with self.db.transaction(write=True) as session:
            session.execute("DELETE FROM content_items WHERE block_type='finance'")
        forecast, _ = self.publish(date(2026, 10, 10), 'taurus')
        self.assertTrue(forecast['guidance']['do'])
        self.assertIsNone(forecast['event'])
        self.assertEqual({metric['label'] for metric in forecast['metrics']}, {'Любовь', 'Работа', 'Энергия'})
        self.assertEqual(forecast['diagnostics']['finance']['reason'], 'no_hard_compatible_approved_content')

    def test_parallel_builds_for_one_sign_date_have_one_immutable_result(self) -> None:
        barrier = threading.Barrier(2)
        def run() -> tuple[str, bool]:
            barrier.wait()
            result, created = self.publish(date(2026, 10, 10), 'gemini')
            return result['publication']['id'], created
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(lambda _: run(), range(2)))
        self.assertEqual(results[0][0], results[1][0])
        self.assertEqual(sum(created for _, created in results), 1)

    def test_export_json_is_frontend_typed_and_test_only_is_excluded(self) -> None:
        for sign in SIGNS:
            self.publish(date(2026, 10, 10), sign)
        output = Path(self.temp.name) / 'horoscopes.json'
        report = write_export(self.db, output)
        document = json.loads(output.read_text(encoding='utf-8'))
        self.assertEqual(report['forecast_count'], 12)
        self.assertEqual(set(document['forecasts']['2026-10-10']), set(SIGNS))
        aries = document['forecasts']['2026-10-10']['aries']
        self.assertEqual(aries['sign'], 'aries')
        self.assertEqual(aries['keyMoment'], None)
        self.assertEqual(aries['event'], None)
        self.assertEqual(aries['metrics'][0]['source_content_version'], 1)
        selections = aries['publication']['content_selections']
        self.assertNotIn('key_moment', selections)
        self.assertNotIn('event_summary', selections)

    def test_dry_run_does_not_create_a_published_forecast(self) -> None:
        forecast, created = build_forecast(self.db, forecast_date=date(2026, 10, 10), sign='aries',
                                           astronomy_snapshot=self.snapshot, events=[], preview=True)
        self.assertFalse(created)
        self.assertIn('forecast_json' if 'forecast_json' in forecast else 'publication', forecast)
        with self.db.transaction() as session:
            count = session.row(session.execute('SELECT COUNT(*) AS count FROM published_forecasts'))['count']
        self.assertEqual(count, 0)


if __name__ == '__main__':
    unittest.main()
