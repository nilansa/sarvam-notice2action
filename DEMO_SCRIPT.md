# Live demo script (60–90 seconds)

Before presenting, start the server with `.venv/bin/python app.py`, confirm the API key is configured privately, and open <http://127.0.0.1:8000/government>. Keep [`samples/government_notice.txt`](samples/government_notice.txt) ready to paste. A live result uses Sarvam API credits and its response time depends on the network and provider.

| Time | Action and narration |
| --- | --- |
| 0:00–0:10 | “Government notices often hide a sequence of offices, documents, and conditions. This page turns one notice into steps while keeping the source evidence visible.” |
| 0:10–0:20 | Paste the included District Revenue Officer notice. Keep the output language set to English, or select Hindi, Telugu, or Bengali. |
| 0:20–0:40 | Submit the notice. As the result appears, point out the ordered actions: collect Form IC-12, fill it and attach the named photocopies, pay the fee and keep the receipt, then submit at Counter 5 during the stated hours. |
| 0:40–1:00 | Show the `source` excerpts. Point to the under-18 parent/guardian ID condition and the missing-photocopy return condition. “These branches come from explicit phrases in the notice.” |
| 1:00–1:20 | Point to `unknowns`: the fee amount is omitted, and processing and certificate collection timing are not given. “The guide should leave these unknown, not guess.” |
| 1:20–1:30 | “This is a non-authoritative reading aid, not an official government service. Check the notice or responsible office for important details.” |

If the result invents a fee, document, office, deadline, or collection date, call it out as an error and do not present that claim as fact. A result that preserves unknowns and quotes the notice is the successful demo outcome.
