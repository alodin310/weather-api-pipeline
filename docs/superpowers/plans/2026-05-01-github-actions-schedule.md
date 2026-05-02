# GitHub Actions Scheduled Weather Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a GitHub Actions workflow that runs `weather.py` daily, verifies the CSV output, and commits the result back to `main`.

**Architecture:** A single workflow file (`.github/workflows/weather-pipeline.yml`) handles scheduling, Python setup, script execution, output verification, and the commit-back loop. `weather.py` requires no changes — it already reads the API key from `os.getenv("WEATHER_API_KEY")`. The GitHub repository secret `WEATHER_API_KEY` must be set manually before the workflow can run successfully.

**Tech Stack:** GitHub Actions, `actions/checkout@v4`, `actions/setup-python@v5`, Python 3.11, bash

---

## File Map

| Action | Path | Responsibility |
|---|---|---|
| Create | `.github/workflows/weather-pipeline.yml` | Full workflow definition |

No other files are created or modified.

---

### Task 1: Create the workflow directory and file

**Files:**
- Create: `.github/workflows/weather-pipeline.yml`

- [ ] **Step 1: Create the directory**

```bash
mkdir -p .github/workflows
```

- [ ] **Step 2: Write the workflow file**

Create `.github/workflows/weather-pipeline.yml` with this exact content:

```yaml
name: Weather Pipeline

on:
  schedule:
    - cron: '0 8 * * *'
  workflow_dispatch:

permissions:
  contents: write

jobs:
  run-pipeline:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run weather pipeline
        env:
          WEATHER_API_KEY: ${{ secrets.WEATHER_API_KEY }}
        run: python weather.py

      - name: Verify output
        run: |
          if [ ! -f weather_data.csv ]; then
            echo "ERROR: weather_data.csv not found"
            exit 1
          fi
          lines=$(wc -l < weather_data.csv)
          if [ "$lines" -lt 2 ]; then
            echo "ERROR: weather_data.csv has $lines line(s), expected header + data"
            exit 1
          fi
          echo "Output verified: $lines lines (including header)"

      - name: Commit and push updated CSV
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add weather_data.csv
          if git diff --staged --quiet; then
            echo "No changes to commit"
          else
            git commit -m "chore: update weather data $(date -u +%Y-%m-%d)"
            git push
          fi
```

- [ ] **Step 3: Validate the YAML syntax locally**

```bash
python -c "import yaml; yaml.safe_load(open('.github/workflows/weather-pipeline.yml')); print('YAML valid')"
```

Expected output:
```
YAML valid
```

If it prints a YAML parse error, fix the indentation before continuing.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/weather-pipeline.yml
git commit -m "feat: add GitHub Actions scheduled weather pipeline"
```

Expected output: one line showing the new file added, e.g. `1 file changed, 48 insertions(+)`.

---

### Task 2: Add the API key as a GitHub repository secret

**Files:** None (GitHub web UI action)

This step must be completed before the workflow can run successfully. The runner has no `.env` file, so `os.getenv("WEATHER_API_KEY")` will return `None` unless the secret is configured.

- [ ] **Step 1: Open the repository secrets page**

Navigate to:
```
https://github.com/alodin310/weather-api-pipeline/settings/secrets/actions
```

- [ ] **Step 2: Create the secret**

Click **New repository secret**.

- **Name:** `WEATHER_API_KEY`
- **Secret:** paste the value from your local `.env` file (the key after `WEATHER_API_KEY=`)

Click **Add secret**.

- [ ] **Step 3: Verify the secret appears in the list**

After saving, the secrets page should list `WEATHER_API_KEY` under Repository secrets. The value is masked — you will not see it again.

---

### Task 3: Push and trigger a manual run

**Files:** None (git and GitHub UI actions)

- [ ] **Step 1: Push to GitHub**

```bash
git push origin main
```

Expected output: something like:
```
To https://github.com/alodin310/weather-api-pipeline.git
   254001d..f5bed1a  main -> main
```

- [ ] **Step 2: Trigger a manual run via workflow_dispatch**

Navigate to:
```
https://github.com/alodin310/weather-api-pipeline/actions/workflows/weather-pipeline.yml
```

Click **Run workflow** → **Run workflow** (branch: `main`).

- [ ] **Step 3: Watch the run complete**

The run should take roughly 2–3 minutes (pip install + 47 API calls with 1-second sleeps). Click into the run to see live logs. All steps should show green checkmarks.

Expected final log lines from the **Verify output** step:
```
Output verified: 330 lines (including header)
```
(47 cities × 7 days = 329 data rows + 1 header = 330 lines)

Expected final log lines from the **Commit and push** step:
```
[main xxxxxxx] chore: update weather data 2026-05-01
```

- [ ] **Step 4: Confirm the commit appeared in the repo**

Navigate to:
```
https://github.com/alodin310/weather-api-pipeline/commits/main
```

The most recent commit should be `chore: update weather data <today's date>` authored by `github-actions[bot]`.

---

## Failure Checklist

If a step fails, check here first:

| Symptom | Likely cause | Fix |
|---|---|---|
| `Run weather pipeline` step fails with `None` API key error | Secret not configured | Complete Task 2 |
| `Run weather pipeline` step fails with HTTP 403 | API key invalid or quota exceeded | Check WeatherAPI.com dashboard |
| `Commit and push` step fails with `403` or `Permission denied` | `permissions: contents: write` missing | Verify it appears at the top level of the workflow file, not inside `jobs` |
| YAML parse error on push | Bad indentation in workflow file | Re-run Step 3 of Task 1 to validate |
| Verify step fails with `1 line(s)` | Script exited early after writing only the header | Check the Run pipeline step logs for API errors |
