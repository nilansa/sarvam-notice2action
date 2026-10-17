"""Bounded import of public Dropbox shared files; never accesses private accounts."""
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener
from doc_ocr import MAX_DOCUMENT_BYTES, valid_document


def _allowed_host(url, initial=False):
    parsed = urlsplit(url)
    hostname = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or parsed.username or parsed.password or parsed.port:
        raise ValueError("Expected a Dropbox HTTPS link")
    if initial:
        if hostname not in {"www.dropbox.com", "dropbox.com"}:
            raise ValueError("A publicly shared Dropbox URL is required.")
        if not (parsed.path.startswith("/s/") or parsed.path.startswith("/scl/fi/")):
            raise ValueError("Link is not a Dropbox shared file.")
    elif hostname not in {"dropbox.com", "dropboxusercontent.com"} and not hostname.endswith((".dropbox.com", ".dropboxusercontent.com")):
        raise ValueError("Unexpected download location")
    return parsed


class _DropboxOnlyRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        _allowed_host(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_shared_document(link):
    parsed = _allowed_host(link, initial=True)
    args = dict(parse_qsl(parsed.query, keep_blank_values=True))
    args["dl"] = "1"
    url = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(args), ""))
    opener = build_opener(_DropboxOnlyRedirects())
    with opener.open(Request(url, headers={"User-Agent": "Notice2Action/1.0"}), timeout=16) as response:
        _allowed_host(response.url)
        data = response.read(MAX_DOCUMENT_BYTES + 1)
    if not data or len(data) > MAX_DOCUMENT_BYTES:
        raise ValueError("Dropbox file is empty or over the 8 MB limit")
    for mime in ("application/pdf", "image/png", "image/jpeg"):
        if valid_document(data, mime):
            return data, mime
    raise ValueError("File is not a PDF, PNG or JPEG.")
