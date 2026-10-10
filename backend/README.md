# ASTRA batch backend

Python 3.10+ prepares immutable daily forecasts for the static Astro frontend. It does not expose an HTTP API or call an LLM.

## Local setup

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r backend/requirements.txt
cp .env.example .env
docker compose up -d postgres
set -a && . ./.env && set +a
```

Place a local JPL DE432s SPK kernel at `data/ephemeris/de432s.bsp` or set `ASTRA_DE432S_PATH` to its path. The kernel is local-only, ignored by Git, and never downloaded at runtime. Without it, `calc` fails closed and does not create events.

## Commands

```sh
python backend/astra.py migrate
python backend/astra.py seed report
python backend/astra.py seed import
python backend/astra.py calc --date 2026-10-10
python backend/astra.py publish --date 2026-10-10
python backend/astra.py diagnose --date 2026-10-10 --sign libra
python backend/astra.py export
python backend/astra.py verify
PYTHONPATH=backend python -m unittest discover -s backend/tests -v
```

`seed report` needs no database and prints actual approved pools by block/sign plus original main-text word counts. Import preserves the complete source row and its hash. Re-import is a no-op for identical `(id, version)`; changing an existing version is rejected. Add an explicitly versioned content record for future updates.

`calc` stores daily positions and calculated events using the local kernel. `publish` requires a saved calculation; repeated publication is unchanged. Use `--republish` only for a deliberate new revision. `export` atomically writes the latest published forecast per sign/date to `src/data/generated/horoscopes.json`; Astro imports that file at build time. No database or astronomical service is called from the user page.

The seed contains 3 approved main texts, 6 entries for each regular block, and one `test_only` entry each for key moments/events. Those two entries are excluded from publication. Main texts are 161–165 words versus the requested 250–350 target; the source wording is preserved and each export/diagnostic carries a length warning. There are no public approved key-moment or event-summary entries, so those optional UI sections are omitted. No long no-repeat window is implied by these pool sizes.
