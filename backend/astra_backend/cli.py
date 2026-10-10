from __future__ import annotations

import argparse
import json
import sys
import uuid
from contextlib import contextmanager
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Iterator

from . import __version__
from .astronomy import ASTRONOMY_ALGORITHM_VERSION, AstronomyUnavailable, calculate_day, load_day, store_day
from .content import SIGNS, load_seed, seed_summary
from .db import Database, utc_now
from .export import write_export
from .forecast import ALGORITHM_VERSION, build_forecast
from .seed import import_seed
from .settings import DATABASE_URL, EXPORT_PATH, SEED_PATH
from .verify import verify_database


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog='astra', description='Подготовка астрономических данных и статических прогнозов ASTRA.')
    root.add_argument('--database-url', default=DATABASE_URL, help='Переопределить DATABASE_URL (для тестов поддерживается sqlite:///).')
    root.add_argument('--version', action='version', version=f'astra-backend {__version__}')
    commands = root.add_subparsers(dest='command', required=True)

    commands.add_parser('migrate', help='Применить SQL-миграции.')
    seed = commands.add_parser('seed', help='Валидировать и импортировать seed-библиотеку.')
    seed_commands = seed.add_subparsers(dest='seed_command', required=True)
    seed_import = seed_commands.add_parser('import', help='Идемпотентно импортировать JSON в PostgreSQL.')
    seed_import.add_argument('--file', type=Path, default=SEED_PATH)
    seed_commands.add_parser('report', help='Показать совместимые пулы и длины исходных текстов без базы.')

    calc = commands.add_parser('calc', help='Рассчитать день по локальному JPL DE432s kernel.')
    calc.add_argument('--date', required=True, type=date.fromisoformat)
    calc.add_argument('--replace', action='store_true', help='Заменить сохранённый расчёт этой версии эфемерид.')

    publish = commands.add_parser('publish', help='Собрать и сохранить неизменяемые прогнозы по сохранённому астроконтексту.')
    publish.add_argument('--date', type=date.fromisoformat)
    publish.add_argument('--from-date', type=date.fromisoformat)
    publish.add_argument('--to-date', type=date.fromisoformat)
    publish.add_argument('--sign', choices=SIGNS)
    publish.add_argument('--republish', action='store_true', help='Создать новую revision, сохранив опубликованную историю.')

    export = commands.add_parser('export', help='Экспортировать опубликованные прогнозы для Astro.')
    export.add_argument('--output', type=Path, default=EXPORT_PATH)

    verify = commands.add_parser('verify', help='Проверить целостность библиотеки и опубликованных прогнозов.')
    verify.add_argument('--file', type=Path, default=SEED_PATH)

    diagnostic = commands.add_parser('diagnose', help='Показать расчёт → правила → кандидаты → причины выбора → JSON.')
    diagnostic.add_argument('--date', required=True, type=date.fromisoformat)
    diagnostic.add_argument('--sign', required=True, choices=SIGNS)
    return root


@contextmanager
def logged_run(database: Database, command: str, run_date: date | None = None) -> Iterator[tuple[str, dict[str, Any]]]:
    database.migrate()
    run_id = str(uuid.uuid4())
    diagnostics: dict[str, Any] = {}
    started = utc_now()
    with database.transaction(write=True) as session:
        session.execute(
            'INSERT INTO algorithm_runs(id, command, run_date, status, started_at, diagnostics_json) VALUES (?, ?, ?, ?, ?, ?)',
            (run_id, command, run_date.isoformat() if run_date else None, 'running', started, '{}'),
        )
    try:
        yield run_id, diagnostics
    except Exception as exc:
        with database.transaction(write=True) as session:
            session.execute(
                'UPDATE algorithm_runs SET status=?, finished_at=?, diagnostics_json=?, error=? WHERE id=?',
                ('failed', utc_now(), json.dumps(diagnostics, ensure_ascii=False), str(exc), run_id),
            )
        raise
    else:
        with database.transaction(write=True) as session:
            session.execute(
                'UPDATE algorithm_runs SET status=?, finished_at=?, diagnostics_json=? WHERE id=?',
                ('succeeded', utc_now(), json.dumps(diagnostics, ensure_ascii=False), run_id),
            )


def _date_range(args: argparse.Namespace) -> list[date]:
    if args.date:
        if args.from_date or args.to_date:
            raise ValueError('Используйте либо --date, либо пару --from-date/--to-date.')
        return [args.date]
    if not args.from_date or not args.to_date:
        raise ValueError('Для publish укажите --date либо обе границы --from-date и --to-date.')
    if args.from_date > args.to_date:
        raise ValueError('--from-date не может быть позже --to-date.')
    days = (args.to_date - args.from_date).days
    if days > 366:
        raise ValueError('Один пакетный запуск ограничен 367 днями.')
    return [args.from_date + timedelta(days=offset) for offset in range(days + 1)]


def _run_publish(database: Database, forecast_date: date, signs: list[str], republish: bool,
                 *, preview: bool = False) -> list[dict[str, Any]]:
    snapshot, events = load_day(database, forecast_date)
    results = []
    for sign in signs:
        export, created = build_forecast(
            database, forecast_date=forecast_date, sign=sign,
            astronomy_snapshot=snapshot, events=events, republish=republish, preview=preview,
        )
        results.append({'forecast_date': forecast_date.isoformat(), 'sign': sign,
                        'status': 'preview' if preview else 'published' if created else 'unchanged',
                        'revision': export['publication']['revision'],
                        'main_word_count': export['publication']['main_word_count'],
                        'fallback_reasons': export['publication']['fallback_reasons']})
    return results


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    database = Database(args.database_url)
    try:
        if args.command == 'migrate':
            print(json.dumps({'applied_migrations': database.migrate()}, ensure_ascii=False, indent=2))
            return 0
        if args.command == 'seed' and args.seed_command == 'report':
            _, items = load_seed(SEED_PATH)
            print(json.dumps(seed_summary(items), ensure_ascii=False, indent=2))
            return 0
        if args.command == 'seed' and args.seed_command == 'import':
            result = import_seed(database, args.file)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        if args.command == 'calc':
            with logged_run(database, 'calc', args.date) as (_, log):
                snapshot = calculate_day(args.date)
                store_day(database, snapshot, replace=args.replace)
                log.update({'local_date': args.date.isoformat(), 'event_count': len(snapshot['events']),
                            'ephemeris_version': snapshot['ephemeris_version'],
                            'algorithm_version': ASTRONOMY_ALGORITHM_VERSION})
            print(json.dumps({'date': args.date.isoformat(), 'event_count': len(snapshot['events']),
                              'ephemeris_version': snapshot['ephemeris_version'], 'status': 'calculated_and_stored'}, ensure_ascii=False, indent=2))
            return 0
        if args.command == 'publish':
            dates = _date_range(args)
            signs = [args.sign] if args.sign else list(SIGNS)
            results = []
            for target in dates:
                with logged_run(database, 'publish', target) as (_, log):
                    batch = _run_publish(database, target, signs, args.republish)
                    log.update({'signs': signs, 'forecasts': batch, 'algorithm_version': ALGORITHM_VERSION})
                    results.extend(batch)
            print(json.dumps({'count': len(results), 'forecasts': results}, ensure_ascii=False, indent=2))
            return 0
        if args.command == 'export':
            result = write_export(database, args.output)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        if args.command == 'verify':
            _, source_items = load_seed(args.file)
            with logged_run(database, 'verify') as (_, log):
                result = verify_database(database)
                result['source_seed'] = seed_summary(source_items)
                log.update({'content_versions': result['content_version_count'], 'forecasts': result['published_forecast_count']})
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        if args.command == 'diagnose':
            snapshot, events = load_day(database, args.date)
            with logged_run(database, 'diagnose', args.date) as (_, log):
                export, _ = build_forecast(database, forecast_date=args.date, sign=args.sign,
                                           astronomy_snapshot=snapshot, events=events, preview=True)
                trace = {'astronomy': snapshot, 'calculated_events': events,
                         'astrology_context': export['astrology'],
                         'candidate_selection': export['diagnostics'],
                         'reasons': export['publication']['fallback_reasons'], 'forecast_json': export}
                log.update({'sign': args.sign, 'content_selection': export['publication']['content_selections']})
            print(json.dumps(trace, ensure_ascii=False, indent=2))
            return 0
    except (ValueError, RuntimeError, OSError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    except Exception as exc:
        print(json.dumps({'error': f'{type(exc).__name__}: {exc}'}, ensure_ascii=False), file=sys.stderr)
        return 1
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
