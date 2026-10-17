"""Bounded Sarvam Document AI OCR; provider details never leave this module."""

from io import BytesIO
import time
import urllib.request
from urllib.parse import urlsplit
from zipfile import ZipFile


MAX_DOCUMENT_BYTES = 8 * 1024 * 1024
DOCUMENT_TYPES = {"image/png": ".png", "image/jpeg": ".jpg", "application/pdf": ".pdf"}
DOCUMENT_LANGUAGES = {"en-IN", "hi-IN", "te-IN", "bn-IN"}


def valid_document(data, mime):
    if mime == "image/png":
        return data.startswith(b"\x89PNG\r\n\x1a\n")
    if mime == "image/jpeg":
        return data.startswith(b"\xff\xd8\xff")
    if mime == "application/pdf":
        return data.startswith(b"%PDF-")
    return False


def digitise_document(data, mime, language, api_key):
    from sarvamai import SarvamAI

    deadline = time.monotonic() + 90

    def remaining():
        seconds = deadline - time.monotonic()
        if seconds <= 0:
            raise TimeoutError("OCR timed out.")
        return seconds

    def options():
        return {"timeout_in_seconds": max(1, int(remaining())), "max_retries": 0}

    client = SarvamAI(api_subscription_key=api_key, follow_redirects=False)
    upload = [("document" + DOCUMENT_TYPES[mime], BytesIO(data), mime)]
    try:
        job = client.doc_ai.digitise(
            file=upload, language=language, output_format="md", request_options=options()
        )
    except TypeError as exc:
        if "unexpected keyword argument 'output_format'" not in str(exc):
            raise
        # The installed SDK predates the output_format keyword; send the same form field.
        job = client.doc_ai.digitise(
            file=upload, language=language,
            request_options={**options(), "additional_body_parameters": {"output_format": "md"}},
        )
    while True:
        status = client.doc_ai.get_status(job_id=job.job_id, request_options=options()).status.lower()
        if status in {"completed", "partially_completed", "partial"}:
            break
        if status in {"failed", "rejected"}:
            raise ValueError("OCR failed.")
        time.sleep(min(2, remaining()))

    download = client.doc_ai.get_download_url(job_id=job.job_id, request_options=options())
    if urlsplit(download.url).scheme != "https":
        raise ValueError("Invalid OCR output.")
    with urllib.request.urlopen(download.url, timeout=remaining()) as response:
        archive = response.read(32 * 1024 * 1024 + 1)
    remaining()
    if len(archive) > 32 * 1024 * 1024:
        raise ValueError("OCR output is too large.")
    parts = []
    with ZipFile(BytesIO(archive)) as output:
        for entry in sorted(output.infolist(), key=lambda item: item.filename):
            if not entry.is_dir() and entry.filename.lower().endswith(".md"):
                with output.open(entry) as markdown:
                    parts.append(markdown.read(48_000).decode("utf-8", errors="replace"))
                if sum(map(len, parts)) >= 12_000:
                    break
    text = "\n\n".join(parts).strip()[:12_000]
    if not text:
        raise ValueError("No OCR text returned.")
    return text
