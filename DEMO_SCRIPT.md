# Live hackathon demo: Notice2Action (90 seconds)

**Public live app:** https://identical-saves-slip-moses.trycloudflare.com/government

| Time | What to do | What to say |
| --- | --- | --- |
| 0:00–0:15 | Open the government workflow link and scroll to **Real government notices**. | “These are genuine government-issued documents, not a generated mockup.” |
| 0:15–0:35 | Click **Use this official notice** on the **NTA NEET-UG 2026** card. | “Sarvam Vision reads the original notice image in English/Hindi and extracts usable text. Review this text before analysis.” |
| 0:35–1:00 | Click **Build my service guide** with English selected; wait for live Sarvam-105B result. | “Here are the actions and document checks in order, with evidence from the notice. Missing steps or deadlines stay unknown.” |
| 1:00–1:20 | Point out **Steps**, **Conditional routes**, **Unknowns**, and **Source excerpt**. | “The model is not permitted to invent an office, deadline, fee, or counter.” |
| 1:20–1:30 | Click **Copy checklist**. | “People get an actionable list in English, Hindi, Telugu, or Bengali.” |

**Optional stronger conditional flow:** Paste the clearly labelled fictional stress-test text at `samples/government_notice.txt`. It includes a minor applicant, missing photocopy failure, several counters, unspecified fee, and unspecified collection date; use it only as a synthetic edge-case test.

**Original, verifiable sources:** [NTA 2026 public notice](https://cdnbbsr.s3waas.gov.in/s37bc1ec1d9c3426357e69acd5bf320061/uploads/2026/01/202601051550861314.pdf) and [UIDAI 2026 Gazette](https://egazette.gov.in/WriteReadData/2026/272354.pdf).

**Before presenting:** Check Mac is awake, localhost:8000 is running, and the Cloudflare tunnel still returns HTTP 200. A temporary tunnel has no uptime guarantee. Public examples are historical and output is not authoritative government advice.
