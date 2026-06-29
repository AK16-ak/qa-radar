# QA Radar

Get a Telegram alert within ~20 minutes of a relevant **QA Automation / SDET / Test Engineering** job going live — from a hand-picked **watchlist** of companies (polled via their ATS: Greenhouse / Lever / Ashby / SmartRecruiters) **plus** broad **discovery** across free job APIs (Adzuna, Remotive, RemoteOK, Arbeitnow, Himalayas, Jobicy, TheMuse). Runs free, 24/7, on GitHub Actions. No server, no cost.

## How it works

Every 20 minutes a GitHub Action runs `main.py`, which:
1. Fetches jobs from each watchlist company's ATS + discovery APIs.
2. Filters by your keyword/location rules in `config.yaml`.
3. Drops anything already alerted (`state/seen.json`).
4. Sends new matches to your Telegram, then commits the updated seen-list.

## One-time setup

### 1. Create a Telegram bot
- Open Telegram, message **@BotFather**, send `/newbot`, follow prompts.
- Copy the **bot token** → this is `TELEGRAM_TOKEN`.
- Send any message to your new bot (so it can DM you).
- Open `https://api.telegram.org/bot<TELEGRAM_TOKEN>/getUpdates` and copy the `"chat":{"id":...}` number → this is `TELEGRAM_CHAT_ID`.

### 2. (Optional) Adzuna keys for broad discovery
- Sign up free at https://developer.adzuna.com → create an app.
- Copy **App ID** → `ADZUNA_APP_ID`, **App Key** → `ADZUNA_APP_KEY`.
- If skipped, discovery still runs all other sources.

### 3. Push to a PUBLIC GitHub repo
Public repos get unlimited free Actions minutes.

```bash
cd qa-radar
git init && git add -A && git commit -m "init qa-radar"
gh repo create qa-radar --public --source=. --push
```

### 4. Add secrets
Repo → **Settings → Secrets → Actions → New repository secret**. Add:
`TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`, and optionally `ADZUNA_APP_ID`, `ADZUNA_APP_KEY`.

### 5. Enable + test
- Repo → **Actions** tab → enable workflows.
- Open the **scan** workflow → **Run workflow** to trigger manually.
- You should get a Telegram message if matching jobs exist.

### 6. (Recommended) Seed first
Avoid an alert flood on first run:

```bash
pip install -r requirements.txt
python main.py --seed
git add state/seen.json && git commit -m "seed seen state" && git push
```

## Customizing

Everything is in **`config.yaml`**:
- `watchlist`: add/remove companies under `greenhouse` / `lever` / `ashby` / `smartrecruiters`.
- `include_keywords`: QA/SDET/automation titles to match.
- `exclude_keywords`: titles to reject (staff, intern, unrelated roles).
- `priority_locations`: locations that get a ⭐ in alerts.
- `strict_location: true`: only alert for priority locations.
- `discovery.enabled: false`: turn off broad discovery.

## Run locally

```bash
pip install -r requirements.txt
python main.py --dry-run          # prints matches instead of sending Telegram
python main.py --seed             # mark all current jobs seen (first-time)
python -m pytest -q               # run the test suite
```

## Target roles

This radar is configured to catch:
- SDET / Software Development Engineer in Test
- QA Engineer / QA Automation Engineer
- Test Automation Engineer
- Quality Assurance Engineer
- Automation Tester / Automation Engineer
- Performance Test Engineer
- Selenium / Cypress / Playwright / Appium roles

## Architecture

```
config.yaml
    │
    ▼
main.py ──► sources/ (13 connectors) ──► filters.py ──► dedup.py ──► notify.py ──► Telegram
                                                             │
                                                      state/seen.json
```
