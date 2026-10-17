# Notice2Action

Notice2Action turns a government notice into a grounded, step-by-step action guide. The government workflow is the main hackathon demo. The earlier general notice explainer is still available as a bonus mode. Select one of 11 guide languages independently of the 23 supported OCR languages.

**Live public demo (temporary Cloudflare tunnel):** [Open Government Workflow](https://identical-saves-slip-moses.trycloudflare.com/government). The link works only while the developer's Mac and the tunnel stay running. **Repository:** [nilansa/sarvam-notice2action](https://github.com/nilansa/sarvam-notice2action).

This is an independent prototype. It is not an official government service and its output is not an authoritative interpretation. Check the original notice or the responsible office whenever a detail matters.

## Government notice workflow

Open <http://127.0.0.1:8000/government> or the public demo link above. **Upload a real PDF/PNG/JPEG, paste an image, or import a publicly shared Dropbox file**, wait for Sarvam Vision to extract the text, then choose English, Hindi, Telugu, or Bengali and build the step-by-step workflow. You can also paste notice text directly.

The OCR API `POST /api/ocr` accepts image/PDF binary data (maximum 8 MB) with its MIME Content-Type and X-Document-Language header (en-IN, hi-IN, te-IN, or bn-IN); it returns JSON with a text field. OCR and workflow analysis use separate Sarvam APIs; document language and response language are separately chosen; this makes it easy to review/correct the OCR text before analysis. The result is designed to follow the stated order of actions and keep the notice's evidence visible:

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

Workflow requests larger than 80 KB and notices longer than 12,000 characters are rejected. The API key stays on the server; it is never sent to the browser. For hosted demos, set the optional private `DEMO_ACCESS_CODE` environment variable. Users must enter that code for any paid analysis/OCR request.

### Authentic government-issued demo scans

Two real government documents are included, each with an original PDF and a PNG preview:

1. [National Testing Agency, 5 January 2026 NEET-UG notice](samples/official/nta_neet_2026.png) — [PDF](samples/official/nta_neet_2026.pdf); official advisory about checking/updating Aadhaar, UDID, and category certificates.
2. [UIDAI Aadhaar Enrolment and Update (First Amendment) Regulations, 2026](samples/official/uidai_aadhaar_2026.png) — [PDF](samples/official/uidai_aadhaar_2026.pdf); official Gazette publication.

Full attribution and original government source URLs: [OFFICIAL_NOTICE_SOURCES.md](OFFICIAL_NOTICE_SOURCES.md). These are **historical demonstrations**, not current advice. In the app, choose **Use this official notice** to OCR the actual scanned preview and then **Build my service guide**. For the UIDAI document, the preview is only page one of a longer PDF.

### Optional synthetic stress test and edge cases

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

Use [DEMO_SCRIPT.md](DEMO_SCRIPT.md) for the live walkthrough. Start with a **real NTA notice PNG**, show live Sarvam Vision OCR, then ask Sarvam-105B to build the workflow. For a stronger branch/unknown-data stress test afterward, paste the separately labelled synthetic example `samples/government_notice.txt`. Live requests consume API credits.

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

A **temporary public Cloudflare Tunnel** is currently used for the live demo; it runs through the local Mac and has no uptime guarantee. The repository now also includes a Python Vercel Functions adapter (`api/index.py`), `vercel.json` routing, and `.vercelignore` that excludes the local `.env`.

To deploy independently on Vercel:
1. Sign into Vercel and import the existing GitHub repository (or run `vercel login` and `vercel --prod` after linking).
2. In Vercel **Project Settings → Environment Variables**, add `SARVAM_API_KEY` as a **private, sensitive** variable and `DEMO_ACCESS_CODE` as another private value. Do not paste either value into code or the README.
3. Deploy on Vercel and open `/government`. The Python Vercel Function serves pages and real notices and handles the Sarvam calls. Full OCR may take up to 90 seconds.
4. Give invited users the demo access code separately; the application prompts for it before paid requests. The deployed Vercel frontend limits uploads to 4 MB due to serverless body-size constraints.

The Vercel project **requires account authorization**; having this deployment configuration in GitHub does not itself create a Vercel deployment. Alternative Python hosts may run `python app.py` using `PORT`.

Never commit, publish, or log the API key. Anonymous Dropbox **shared-file links** are supported; private Dropbox account browsing needs a separate OAuth connection.

The prototype has lightweight in-memory abuse throttling (8 requests per IP per minute and 40 globally). Set `DEMO_ACCESS_CODE` for public access control; leaving it unset makes paid endpoints accessible to anyone who finds the URL. Do not rely on the temporary tunnel for long-term public hosting; consider stronger abuse protection before a permanent deployment.

## Privacy and limitations

- Submitted notice text is sent to Sarvam AI to generate the requested result. Do not submit personal, confidential, or sensitive information.
- The server does not write submitted notice text or the API key to app logs; provider failures are returned as a generic error.
- This is a non-authoritative summary, not a government service or legal/administrative advice. Always verify important instructions with the source notice or responsible office.
- The model can misunderstand poor OCR, mixed-language text, abbreviations, or ambiguous instructions. Human review is required.
- PDF/PNG/JPEG upload uses Sarvam Vision. The original file is previewed alongside editable OCR results; OCR may have errors. The local upload limit is 8 MB; Vercel's is 4 MB. There is no saved history or offline mode. The rate limiter is basic and process-local; public use needs appropriate privacy and security review.

## Existing implementation references

- [Sarvam Chat Completion API](https://docs.sarvam.ai/api/api-guides-tutorials/chat-completion/overview) — model IDs, Python SDK, JSON mode, and response parsing.
- [Sarvam Developer Quickstart](https://docs.sarvam.ai/api/getting-started/quickstart) — API key setup and SDK installation.

- [Sarvam Vision Document AI](https://docs.sarvam.ai/api/api-guides-tutorials/document-intelligence/overview) — real scans/PDFs OCR.
