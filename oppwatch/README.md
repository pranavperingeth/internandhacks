# Weekly Opportunity Watcher ("oppwatch")

A lightweight personal CLI program that collects hackathons and internships from RSS feeds, JSON APIs, and HTML pages once a week, deduplicates listings, filters by interest keywords and locations, remembers seen opportunities in a local SQLite database, and delivers a clean digest of new items via Console, Telegram, or Email.

---

## Features
- **Multi-source ingestion**: Supports RSS/Atom feeds, REST JSON endpoints (with nested dot-paths and filters), and plain HTML scraping with CSS selectors.
- **Deduplication**: Canonicalizes URLs (stripping tracking query params like `utm_*`, `ref`, `fbclid`, etc.) and calculates stable hashes.
- **Customizable scoring**: Keyword match scoring with whole-word regex, location bonuses, exclude keywords, deadline pruning, and age filtering.
- **Seen memory**: Tracks notified items in SQLite (`data/seen.db`) so you never get notified twice for the same opportunity.
- **Fault-tolerant**: If a source fails or gets rate-limited, the run logs the error and continues without crashing.
- **Multiple notifiers**: Output to Console, Telegram Bot, or SMTP Email with automatic message splitting.
- **Optional local LLM**: Uses Ollama (e.g. `qwen2.5:7b`) to verify student relevance, extract deadlines, and generate 1-sentence summaries.

---

## Setup

### 1. Requirements
- Python 3.11+
- Virtual environment

### 2. Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` to configure your notifier and paths:
```env
# Notification channel: console | telegram | email
NOTIFIER=console

# Telegram settings (if NOTIFIER=telegram)
TELEGRAM_BOT_TOKEN=your-bot-token-here
TELEGRAM_CHAT_ID=your-chat-id-here

# Email settings (if NOTIFIER=email)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_TO=recipient@gmail.com

# Database path (default: data/seen.db)
DB_PATH=data/seen.db

# Optional Local LLM (Phase 11)
OLLAMA_MODEL=
```

---

## Commands

```bash
# Run the pipeline (fetches sources, filters, saves new items to DB, and sends digest)
python -m oppwatch run

# Dry-run: fetches, filters, prints digest to terminal WITHOUT marking items as notified
python -m oppwatch run --dry-run

# Run only a specific source by name
python -m oppwatch run --only reddit_internships

# List all enabled sources
python -m oppwatch list-sources

# Reset the seen database
python -m oppwatch reset-db
```

---

## How to Add a Source

Edit `config/sources.yaml`. Add a source under `sources:`.

### 1. RSS Source
```yaml
  - name: my_rss_feed
    type: rss
    kind: hackathon   # hackathon | internship | other
    enabled: true
    url: "https://example.com/feed.xml"
```

### 2. JSON API Source
```yaml
  - name: my_api
    type: json_api
    kind: internship
    enabled: true
    url: "https://api.example.com/jobs"
    params: { "role": "intern", "page": "1" }
    items_path: "data.jobs"       # dot path to the items list (empty string for root array)
    where: { "active": true }     # optional: filter items where key == value
    field_map:
      title: "job_title"
      url: "apply_link"
      org: "company.name"
      location: "locations"       # lists are joined with ", "
      deadline: "expires_at"
```

### 3. Plain HTML Source
```yaml
  - name: my_html_site
    type: html
    kind: hackathon
    enabled: true
    url: "https://example.com/hackathons"
    item_selector: "div.hackathon-card"
    fields:
      title: "h3.title"
      url: "a.event-link"         # href is extracted and resolved to absolute URL
      org: "span.organizer"
      deadline: "span.deadline-date"
```

---

## Scheduling

### Option A: cron (Linux / macOS)
To run every Monday at 09:00:
```cron
0 9 * * MON cd /full/path/to/oppwatch && .venv/bin/python -m oppwatch run >> data/run.log 2>&1
```

### Option B: GitHub Actions
A workflow is provided in `.github/workflows/weekly.yml`. In your GitHub repository:
1. Set repository secrets: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.
2. The workflow runs weekly on schedule (Monday 09:00 IST), executes `python -m oppwatch run`, and commits `data/seen.db` back to the repository.

---

## Troubleshooting

- **Source returned 0 items**: Check `config/sources.yaml` against the real payload. For JSON APIs, verify `items_path` and `field_map` keys match the server's response.
- **HTTP 429 / 403 (Rate Limiting)**: Websites like Reddit rate-limit frequent requests. The scraper includes backoff retries and sequential delays, but do not run multiple scans within seconds.
- **HTML source returns empty listings**: Many modern job boards (Unstop, Devfolio, Internshala) render content dynamically via JavaScript. Open DevTools in your browser -> Network tab -> filter "Fetch/XHR", locate the underlying JSON endpoint, and add it as a `json_api` source.
- **Opportunities not appearing**: Check `config/filters.yaml`. Verify that `min_score` is not too high, or check if an `exclude_keywords` rule matched.

---

## Contributing

Contributions are welcome! Please check out [CONTRIBUTORS.md](CONTRIBUTORS.md) for contribution guidelines, code standards, and how to add new opportunity sources.

