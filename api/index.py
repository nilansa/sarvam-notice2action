"""Vercel Python Function adapter for the existing stdlib server.

The Vercel rewrite adds ?route=<original path>. All business logic stays in
app.NoticeHandler, so local and hosted behavior share the same implementation.
"""
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import NoticeHandler


class handler(NoticeHandler):
    def _set_original_path(self):
        path = urlsplit(self.path)
        original = parse_qs(path.query).get("route", [])
        if original:
            self.path = "/" + original[0].lstrip("/")
        elif path.path in {"/api/index", "/api/index.py"}:
            self.path = "/"

    def do_GET(self):
        self._set_original_path()
        return super().do_GET()

    def do_POST(self):
        self._set_original_path()
        return super().do_POST()
