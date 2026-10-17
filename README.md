# Notice2Action

Notice2Action turns a government notice into a grounded, step-by-step action guide. The government workflow is the main hackathon demo. The earlier general notice explainer is still available as a bonus mode.

This is an independent prototype. It is not an official government service and its output is not an authoritative interpretation. Check the original notice or the responsible office whenever a detail matters.

## Government notice workflow

Open <http://127.0.0.1:8000/government>, paste a notice, choose English, Hindi, Telugu, or Bengali, and submit. The result is designed to follow the stated order of actions and keep the notice's evidence visible:

- Each step follows the order and sequence stated in the notice. The guide does not invent an office, counter, prerequisite, fee, document, date, or expected outcome.
- `source` contains a short exact supporting phrase from the notice, or an empty string when no phrase supports that field. It is evidence for the stated detail, not a guarantee that the notice itself is current or correct.
- Missing or unclear details go in `unknowns`. Other unknown fields stay empty (`""` or `[]`); the workflow does not fill them with guesses.
- Notice conditions are represented as `branches`, and stated time limits as `deadlines`. A time or date is not called a deadline unless the notice says it is one.
- The notice is untrusted input. Instructions embedded in it cannot change the extraction rules or request hidden system information. The output distinguishes what the notice states from unresolved details and assumptions; assumptions are not presented as facts.

### Output contract

`POST /api/government` returns one JSON object with exactly these fields:

```text
service: string
plain_language: string
preparation: string[]
steps: { number: integer, title: string, office: string, action: string,
         documents: string[], prerequisite: string, when: string, fee: string,
         outcome: string, mistakes: string[], source: string }[]
branches: { condition: string, path: string }[]
deadlines: string[]
unknowns: string[]
final_check: string[]
```

The request contains the notice text and a language code: `en`, `hi`, `te`, or `bn`. For example:

```json
{"notice":"Paste the notice text here","language":"en"}
```

The response uses the selected language. The schema has no extra fields; an unknown step value is an empty string or list, with unresolved questions collected in `unknowns`.

Requests larger than 80 KB and notices longer than 12,000 characters are rejected. The API key stays on the server; it is never sent to the browser.

### Demo notice and edge cases

The supplied example is in [`samples/government_notice.txt`](samples/government_notice.txt). It states that applicants collect Form IC-12, attach specified photocopies, pay a service fee, retain the receipt, and submit at Counter 5 during stated hours. Its conditions and gaps are useful for checking grounded output:

- Applicants under 18 must attach a parent/guardian ID.
- A missing photocopy means the application is returned.
- The fee amount is not stated; do not invent one.
- Processing time and the certificate collection date will be communicated on the acknowledgment. Do not invent either date.
- “Working days” is not defined in the notice. Do not guess which days the office is open.
- The notice does not state extra documents, payment methods, or a certificate pickup counter. Do not add them.

The guide is a reading aid. Recheck the source notice and confirm unresolved administrative details with the responsible office.

## Run locally

Requirements: Python 3.9 or newer and [`uv`](https://docs.astral.sh/uv/).

```sh
cd /Users/nilan/Documents/sarvam-notice2action
uv venv
uv pip install --python .venv/bin/python -r requirements.txt
```

Create `.env` in the project root and add a key from the [Sarvam dashboard](https://dashboard.sarvam.ai/). The real key is a local secret and must stay out of Git; `.env` is excluded by `.gitignore`. Restrict local file permissions with `chmod 600 .env`:

```dotenv
SARVAM_API_KEY=your_real_key_here
```

Keep the key private. Start the app:

```sh
.venv/bin/python app.py
```

Open <http://127.0.0.1:8000>. Stop the server with `Ctrl+C` in its terminal.

## 60–90 second live demo

Use the timed walkthrough in [`DEMO_SCRIPT.md`](DEMO_SCRIPT.md). Start the app before presenting, then open `/government`, load the included notice, select a language, and submit it. Point out the ordered steps, exact source excerpts, minor-applicant branch, and the explicitly unknown fee amount and collection timing. The live request depends on network and provider response time.

## Bonus: general notice explainer

The home page at <http://127.0.0.1:8000/> keeps the earlier, broader notice explainer. Select an output language, paste a notice or click **Try a sample notice**, then click **Explain this notice**. It returns a summary, actions, dates, deadlines, caveats, and a short shareable message. Its endpoint is `POST /api/analyze` with a JSON body such as:

```json
{"notice":"Paste notice text here","language":"en"}
```

The app supports English, Hindi, Telugu, and Bengali in both workflows.

## Tests and smoke check

Run the government workflow's HTTP tests with:

```sh
.venv/bin/python -m unittest discover -s tests -v
```

They cover page serving, request validation, language selection, the API-key error path, and the workflow response. Workflow generation is mocked, so these tests do not make a Sarvam request. For a manual end-to-end check, use the supplied sample and confirm the age condition, missing-copy consequence, omitted fee amount, and unprovided processing/collection date. Check that unknown values stay empty and every source excerpt is an exact phrase from the input.

The existing provider smoke script makes one real Sarvam request:

```sh
.venv/bin/python smoke.py
```

This checks provider connectivity and key configuration; it is not an automated test of the government workflow. It uses API credits and may incur provider charges. Check current Sarvam pricing and account limits before a live demo. No prices are assumed in this README.

## Deployment

No public deployment is confirmed. To deploy after obtaining an API key, use a Python web-service host that can install `requirements.txt`, run `python app.py`, and provide `SARVAM_API_KEY` through its private secret or environment-variable setting. The app reads `PORT` when the host supplies it. Never place a real key in source control, a committed deployment file, or build logs.

Before making the service public, check current provider costs and usage limits and add suitable access controls and abuse protection. The current prototype has no authentication or per-user rate limiting.

## Privacy and limitations

- Submitted notice text is sent to Sarvam AI to generate the requested result. Do not submit personal, confidential, or sensitive information.
- The server does not write submitted notice text or the API key to app logs; provider failures are returned as a generic error.
- This is a non-authoritative summary, not a government service or legal/administrative advice. Always verify important instructions with the source notice or responsible office.
- The model can misunderstand poor OCR, mixed-language text, abbreviations, or ambiguous instructions. Human review is required.
- The prototype has no document upload, saved history, authentication, rate limiting, or offline mode. Public use needs appropriate privacy and security review.

## Existing implementation references

- [Sarvam Chat Completion API](https://docs.sarvam.ai/api/api-guides-tutorials/chat-completion/overview) — model IDs, Python SDK, JSON mode, and response parsing.
- [Sarvam Developer Quickstart](https://docs.sarvam.ai/api/getting-started/quickstart) — API key setup and SDK installation.
