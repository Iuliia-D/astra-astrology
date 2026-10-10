from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEED_PATH = ROOT / 'data' / 'seed' / 'astra_seed_content_v1.json'
MIGRATIONS_PATH = ROOT / 'backend' / 'migrations'
EXPORT_PATH = ROOT / 'src' / 'data' / 'generated' / 'horoscopes.json'
DATABASE_URL = os.getenv(
    'DATABASE_URL', 'postgresql://astra:astra@localhost:5432/astra'
)
EPHEMERIS_PATH = Path(os.getenv('ASTRA_DE432S_PATH', ROOT / 'data' / 'ephemeris' / 'de432s.bsp'))
TIMEZONE = 'Europe/Moscow'
