from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from .content import SIGNS
from .db import Database
from .forecast import latest_forecasts
from .settings import EXPORT_PATH

EXPORT_SCHEMA_VERSION = '1.0.0'


def frontend_document(database: Database) -> dict[str, Any]:
    forecasts = latest_forecasts(database)
    by_date: dict[str, dict[str, Any]] = {}
    for forecast in forecasts:
        day = forecast['forecast_date']
        sign = forecast['sign']
        if sign not in SIGNS:
            raise ValueError(f'Неизвестный знак в опубликованном прогнозе: {sign}')
        by_date.setdefault(day, {})[sign] = forecast
    for day, items in by_date.items():
        for forecast in items.values():
            if forecast.get('publication', {}).get('timezone') != 'Europe/Moscow':
                raise ValueError(f'У {day}/{forecast["sign"]} неверная временная зона.')
    return {'schema_version': EXPORT_SCHEMA_VERSION, 'source': 'astra-static-forecast-export', 'forecasts': by_date}


def write_export(database: Database, output_path: Path = EXPORT_PATH) -> dict[str, Any]:
    document = frontend_document(database)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(document, ensure_ascii=False, indent=2) + '\n'
    temporary: str | None = None
    try:
        with NamedTemporaryFile('w', encoding='utf-8', dir=output_path.parent, delete=False) as target:
            temporary = target.name
            target.write(payload)
            target.flush()
            os.fsync(target.fileno())
        os.replace(temporary, output_path)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)
    return {'output': str(output_path), 'forecast_count': sum(len(items) for items in document['forecasts'].values()),
            'dates': sorted(document['forecasts']), 'schema_version': EXPORT_SCHEMA_VERSION}
