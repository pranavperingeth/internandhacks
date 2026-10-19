# Contributors & Contribution Guide

Thank you for your interest in improving **oppwatch** (Weekly Opportunity Watcher)! 

Whether you are adding new hackathon/internship sources, refining keyword filters, introducing new notification adapters, or improving test coverage, all contributions are warmly welcomed.

---

## 🌟 Contributors

A huge thank you to everyone who has contributed to making **oppwatch** better:

- [@pranavperingeth](https://github.com/pranavperingeth) — Project creator and maintainer

*(Add your name and GitHub handle here when you make your first pull request!)*

---

## 🚀 How to Contribute

Here are the highest-impact areas where you can help:

### 1. Adding New Sources (`config/sources.yaml`)
We want to cover the best high-signal, spam-free opportunities for students:
- **Verified RSS feeds**: Subreddits, blogs, career portals.
- **Public JSON APIs**: Official job boards, hackathon aggregators (Devpost, MLH, Unstop API endpoints, etc.).
- **HTML Scrapers**: Clean listing pages with stable CSS selectors.

*Tip: Make sure the source doesn't require authentication or anti-bot bypasses.*

### 2. Improving Filtering & Scoring (`config/filters.yaml`)
- Expand technical domains (e.g., Systems Engineering, Web3, DevOps, Robotics).
- Refine exclusion keywords to eliminate job-spam, spam promotions, and unpaid ambassadorships.
- Add additional regional hubs and remote location synonyms.

### 3. Adding New Notifiers (`oppwatch/notifiers/`)
Currently supported: `console`, `telegram`, `email_smtp`.
Wanted adapters:
- Discord Webhooks
- Slack Incoming Webhooks
- Matrix / Element
- Desktop notifications (notify-send, osascript)

Each notifier only needs to implement:
```python
def send(text: str) -> bool:
    """Send text. Return True on success, False on failure. Never raise."""
```

### 4. Improving Test Coverage & Robustness
- Add new fixtures in `tests/fixtures/` for real-world API payloads.
- Improve error recovery and rate-limit handling.

---

## 🛠️ Development Setup

1. **Fork and clone** the repository:
   ```bash
   git clone https://github.com/<your-username>/internandhacks.git
   cd internandhacks/oppwatch
   ```

2. **Set up a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Verify the test suite**:
   ```bash
   pytest -q
   ```
   All tests should pass without making any external network requests.

4. **Run a safe dry run**:
   ```bash
   cp .env.example .env
   python -m oppwatch run --dry-run
   ```

---

## 📋 Code Standards

To keep the codebase maintainable, readable, and clean:

- **Type Hints**: Provide type hints on all function signatures (`def func(arg: str) -> bool:`).
- **Docstrings**: Include a clear, one-line docstring for every function.
- **File Length**: Keep files under 150 lines. If a module grows larger, split helper functions cleanly.
- **Dependencies**: Rely on standard library wherever possible. Avoid adding heavyweight external dependencies.
- **Offline Tests**: Tests must NEVER make live internet calls. Use `monkeypatch` and local fixtures in `tests/fixtures/`.
- **Fault Tolerance**: Network calls must be wrapped in `try/except` and logged. One failing source must never crash the entire pipeline.
- **Security**: Never commit secrets, passwords, or bot tokens. All credentials must come from environment variables.

---

## 🔄 Pull Request Checklist

Before submitting a pull request:
- [ ] Run `pytest -q` and ensure all tests pass.
- [ ] Add unit tests for any new feature or bug fix.
- [ ] Update `README.md` or `config/*.yaml` comments if changing configurations or commands.
- [ ] Add your name/handle to the **Contributors** list above!

Happy hacking! 🚀
