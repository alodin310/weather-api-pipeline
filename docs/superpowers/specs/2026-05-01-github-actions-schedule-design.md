# GitHub Actions Scheduled Weather Pipeline

**Date:** 2026-05-01
**Status:** Approved

## Overview

Add a GitHub Actions workflow that runs `weather.py` on a daily schedule, commits the resulting `weather_data.csv` back to the repository, and fails loudly when the output is missing or empty.

## Triggers

| Trigger | Value |
|---|---|
| Scheduled | `cron: '0 8 * * *'` (daily at 08:00 UTC) |
| Manual | `workflow_dispatch` (run from GitHub Actions UI) |

## Permissions

The workflow requires `permissions: contents: write` so the `github-actions[bot]` can push the updated CSV back to `main`. GitHub Actions defaults to `contents: read`, which would cause the push step to fail without this declaration.

## Job: `run-pipeline`

Runs on `ubuntu-latest`.

### Steps

1. **Checkout** — `actions/checkout@v4`
2. **Setup Python** — `actions/setup-python@v5`, version `3.11`, pip cache enabled
3. **Install dependencies** — `pip install -r requirements.txt`
4. **Run pipeline** — `python weather.py` with `WEATHER_API_KEY` injected from repository secret
5. **Verify output** — shell script; exits 1 if `weather_data.csv` is missing or empty
6. **Commit & push** — configures `github-actions[bot]` author, stages `weather_data.csv`, skips commit if file is unchanged, pushes to `main`

## Credentials

`WEATHER_API_KEY` stored as a GitHub repository secret (Settings → Secrets and variables → Actions → New repository secret). Referenced in the workflow as `${{ secrets.WEATHER_API_KEY }}` and scoped to the run-pipeline step only.

No code change required: `weather.py` already reads the key via `os.getenv("WEATHER_API_KEY")`. The `load_dotenv()` call is harmless when no `.env` file is present.

## Success Criteria

A run is green when all three conditions hold:
1. `python weather.py` exits with code 0
2. `weather_data.csv` exists and is non-empty
3. The git push completes without error

## Failure Handling

- Any failed step marks the workflow run as failed
- GitHub sends a failure notification email to the repository owner by default
- The explicit verify step (step 5) catches silent failures where the script exits 0 but produced no usable output

## Output Strategy

`weather_data.csv` is committed back to `main` on every successful run. The file is overwritten each time (not appended), so the repo always contains the latest 7-day forecast snapshot. Git history preserves all prior snapshots.

## Files Created

| File | Purpose |
|---|---|
| `.github/workflows/weather-pipeline.yml` | The workflow definition |

No other files are added or modified.
