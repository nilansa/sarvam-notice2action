# Notice2Action

Notice2Action turns a pasted campus or official notice into a short explanation and a practical action brief. It is a small hackathon demo built with Python's standard library, one HTML page, and Sarvam AI's Python SDK.

## What it does

- Explains a notice in English, Hindi, Telugu, or Bengali.
- Shows a concise summary, concrete actions, dates stated in the notice, stated deadlines, caveats, and a WhatsApp-ready message.
- Explicitly flags **“No deadline stated in this notice”** when no deadline is provided.
- Includes a demo notice, loading and error feedback, a character limit, and a copy button.
- Keeps the API key on the server. The browser never receives it.

## Run locally

Requirements: Python 3.9 or newer and [`uv`](https://docs.astral.sh/uv/).

```sh
cd /Users/nilan/Documents/sarvam-notice2action
uv venv
uv pip install --python .venv/bin/python -r requirements.txt
```

Create or open `.env` at the project root and put your key from the [Sarvam dashboard](https://dashboard.sarvam.ai/) after the equals sign. The local handoff includes a blank template, but `.env` is intentionally not committed, so create it when cloning the repository. Restrict its local permissions with `chmod 600 .env`:

```dotenv
SARVAM_API_KEY=your_real_key_here
```

Keep the key private. `.env` is excluded by `.gitignore`. Then start the app:

```sh
.venv/bin/python app.py
```

Open <http://127.0.0.1:8000>. To stop the server, press `Ctrl+C` in the terminal.

### Demo flow

1. Select an output language.
2. Click **Try a sample notice** or paste a notice. The sample includes an event date and a contact instruction but no stated submission deadline.
3. Click **Explain this notice**. Review the summary, actions, dates, deadline flag, and caveats.
4. Copy the short message for sharing.

## API

`POST /api/analyze` accepts a JSON object with a notice and one of the supported language codes:

```json
{"notice":"Paste notice text here","language":"en"}
```

The response is JSON with `summary`, `actions`, `dates`, `deadlines`, `caveats`, and `whatsapp_message`. The server limits notices to 12,000 characters and rejects request bodies larger than 80 KB, allowing for multi-byte Indic text. It serves the same-origin page and API from one process, with no CORS or database layer.

## Architecture

- `app.py` serves `static/index.html` using `ThreadingHTTPServer` and handles `POST /api/analyze`.
- The handler validates request size, text, and language, then calls `SarvamAI.chat.completions` using `sarvam-105b-conversations` and JSON mode.
- The model is asked to distinguish dates from deadlines and to leave deadline items empty when the notice states none. The server parses and checks the returned JSON fields before sending them to the page.
- The browser builds result lists with `textContent`, so notice/model text is displayed as text rather than executable HTML.
- The `.env` loader reads only `SARVAM_API_KEY` and does not replace a key already set in the process environment.

## API key and privacy

Do not commit, paste into an issue, or share the contents of `.env`. The provided `.env` starts with exactly `SARVAM_API_KEY=` and contains no placeholder credential. The application returns a setup message without contacting Sarvam while the value is empty. API errors are returned as a generic message; submitted notice text and the key are not written to app logs. A notice is sent to Sarvam AI for analysis, so do not submit personal, confidential, or sensitive information.

## Smoke call

After adding your real key and installing the dependency, this makes one live chat-completion call and prints the reply:

```sh
.venv/bin/python smoke.py
```

It exits without making a request if the key is missing.

## Deployment

The server reads `PORT` when provided and binds to `0.0.0.0` for a hosting service; without `PORT`, it binds only to `127.0.0.1` for local use. A Python web-service host can install `requirements.txt`, start `python app.py`, and supply `SARVAM_API_KEY` through its private environment-variable or secret setting. Never put a real key in a deployment file, repository variable committed to source, or build log. Set usage limits and review the provider's current pricing before a public demo; this prototype has no authentication or per-user rate limiting.

## Known limitations

- This is an aid for reading, not an authoritative interpretation. Always check the source notice for important dates, eligibility, or official instructions.
- The model may misunderstand text, especially low-quality OCR, mixed-language text, or ambiguous abbreviations. The prompt asks it not to infer missing facts, but generated output still needs human review.
- There is no image/PDF upload, persistent history, authentication, rate limiting, or offline mode. Input stays in the page until it is replaced or the page is closed; each analysis is sent to Sarvam.
- The local server is intended for a single-user demo. Public deployment needs access controls, abuse protection, and an appropriate privacy review.

## Sarvam references

- [Chat Completion API](https://docs.sarvam.ai/api/api-guides-tutorials/chat-completion/overview) — V1 model IDs, Python SDK call, JSON mode, and response parsing.
- [Developer Quickstart](https://docs.sarvam.ai/api/getting-started/quickstart) — API key setup and SDK installation.
