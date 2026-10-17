"""HTTP integration tests for the government notice workflow."""

import json
import os
import socket
import sys
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import app
import gov_workflow


NOTICE = (
    "Office of the District Revenue Officer. For income certificate attestation, "
    "applicants must first collect Form IC-12 at the Reception Desk, Ground Floor. "
    "Fill the form and attach photocopies of Aadhaar and income proof. Applicants "
    "under 18 must also attach a parent/guardian ID. Pay the stated service fee at "
    "the Cash Counter, First Floor (the amount is not specified in this notice), "
    "retain the receipt, then submit the filled form with receipt at Counter 5, "
    "Second Floor between 10 AM and 2 PM on working days. Staff will issue an "
    "acknowledgment slip. If any photocopy is missing, the application will be "
    "returned. Processing time and certificate collection date will be communicated "
    "on the acknowledgment."
)

WORKFLOW = {
    "service": "Income certificate attestation",
    "plain_language": (
        "Collect and complete Form IC-12, attach the required photocopies, pay the "
        "fee, and submit the form with the receipt during the stated hours."
    ),
    "preparation": [
        "Photocopy of Aadhaar",
        "Photocopy of income proof",
        "Parent/guardian ID photocopy if the applicant is under 18",
    ],
    "steps": [
        {
            "number": 1,
            "title": "Collect the form",
            "office": "Reception Desk, Ground Floor",
            "action": "Collect Form IC-12.",
            "documents": [],
            "prerequisite": "",
            "when": "",
            "fee": "",
            "outcome": "Form IC-12",
            "mistakes": [],
            "source": "first collect Form IC-12 at the Reception Desk, Ground Floor",
        },
        {
            "number": 2,
            "title": "Complete the form and attach copies",
            "office": "",
            "action": "Fill the form and attach photocopies of Aadhaar and income proof.",
            "documents": ["Photocopy of Aadhaar", "Photocopy of income proof"],
            "prerequisite": "Form IC-12",
            "when": "",
            "fee": "",
            "outcome": "A filled form with the required photocopies",
            "mistakes": ["A missing photocopy will cause the application to be returned."],
            "source": "If any photocopy is missing, the application will be returned",
        },
        {
            "number": 3,
            "title": "Pay the service fee",
            "office": "Cash Counter, First Floor",
            "action": "Pay the stated service fee and retain the receipt.",
            "documents": [],
            "prerequisite": "",
            "when": "",
            "fee": "Amount not specified in the notice",
            "outcome": "Payment receipt",
            "mistakes": [],
            "source": "Pay the stated service fee at the Cash Counter, First Floor",
        },
        {
            "number": 4,
            "title": "Submit the application",
            "office": "Counter 5, Second Floor",
            "action": "Submit the filled form with the receipt.",
            "documents": ["Filled Form IC-12", "Payment receipt"],
            "prerequisite": "",
            "when": "10 AM to 2 PM on working days",
            "fee": "",
            "outcome": "Acknowledgment slip",
            "mistakes": [],
            "source": "submit the filled form with receipt at Counter 5, Second Floor",
        },
    ],
    "branches": [
        {
            "condition": "The applicant is under 18.",
            "path": "Also attach a parent/guardian ID photocopy.",
        }
    ],
    "deadlines": ["Submission hours: 10 AM to 2 PM on working days."],
    "unknowns": [
        "The service fee amount is not specified.",
        "Processing time and certificate collection date are not stated; the notice says they will be communicated on the acknowledgment.",
    ],
    "final_check": [
        "Attach photocopies of Aadhaar and income proof.",
        "If the applicant is under 18, also attach a parent/guardian ID photocopy.",
        "Keep the payment receipt and submit it with the filled form.",
    ],
}


class GovernmentHTTPTests(unittest.TestCase):
    def request(self, method, path, body=None):
        client, handler_socket = socket.socketpair()

        def serve_request():
            try:
                app.NoticeHandler(handler_socket, ("local", 0), None)
            finally:
                handler_socket.close()

        handler = threading.Thread(
            target=serve_request,
            daemon=True,
        )
        handler.start()
        client.settimeout(3)
        headers = ["Host: local", "Connection: close"]
        if body is not None:
            headers.extend(
                ("Content-Type: application/json", f"Content-Length: {len(body)}")
            )
        request = f"{method} {path} HTTP/1.1\r\n" + "\r\n".join(headers) + "\r\n\r\n"
        client.sendall(request.encode("ascii") + (body or b""))
        response_bytes = bytearray()
        while True:
            try:
                chunk = client.recv(65536)
            except socket.timeout:
                client.close()
                self.fail("HTTP handler did not close its response")
            if not chunk:
                break
            response_bytes.extend(chunk)
        client.close()
        handler.join(timeout=3)
        if handler.is_alive():
            self.fail("HTTP handler thread did not finish")
        head, response_body = bytes(response_bytes).split(b"\r\n\r\n", 1)
        lines = head.decode("iso-8859-1").split("\r\n")
        status = int(lines[0].split(" ", 2)[1])
        response_headers = dict(line.split(": ", 1) for line in lines[1:])
        return status, response_headers, response_body

    def post_json(self, payload):
        return self.request("POST", "/api/government", json.dumps(payload).encode("utf-8"))

    def mock_generator(self, mocked):
        """Patch both supported import styles used by the app route."""
        return (
            patch.object(gov_workflow, "generate_workflow", mocked),
            patch.object(app, "generate_workflow", mocked, create=True),
        )

    def test_get_home_and_government_pages(self):
        for path in ("/", "/government"):
            with self.subTest(path=path):
                status, headers, body = self.request("GET", path)
                self.assertEqual(status, 200)
                self.assertIn("text/html", headers.get("Content-Type", ""))
                self.assertTrue(body.strip(), f"{path} returned an empty page")

    def test_post_returns_workflow_and_normalizes_language(self):
        mocked = Mock(return_value=WORKFLOW)
        module_patch, app_patch = self.mock_generator(mocked)
        with patch.dict(os.environ, {"SARVAM_API_KEY": "unit-test-placeholder"}), \
                patch.object(app, "load_dotenv"), module_patch, app_patch:
            status, headers, body = self.post_json({"notice": NOTICE, "language": "hi"})

        self.assertEqual(status, 200)
        self.assertIn("application/json", headers.get("Content-Type", ""))
        self.assertEqual(json.loads(body), WORKFLOW)
        mocked.assert_called_once_with(NOTICE, "Hindi")

    def test_invalid_inputs_are_rejected_without_running_workflow(self):
        invalid_bodies = (
            b"not-json",
            b"{}",
            json.dumps({"notice": "", "language": "en"}).encode("utf-8"),
            json.dumps({"notice": 12, "language": "en"}).encode("utf-8"),
            json.dumps({"notice": NOTICE, "language": "fr"}).encode("utf-8"),
        )
        mocked = Mock(return_value=WORKFLOW)
        module_patch, app_patch = self.mock_generator(mocked)
        with patch.dict(os.environ, {"SARVAM_API_KEY": "unit-test-placeholder"}), \
                patch.object(app, "load_dotenv"), module_patch, app_patch:
            for body in invalid_bodies:
                with self.subTest(body=body[:40]):
                    status, _, _ = self.request(
                        "POST", "/api/government", body=body
                    )
                    self.assertEqual(status, 400)

        mocked.assert_not_called()

    def test_missing_api_key_blocks_workflow_generation(self):
        sarvam_constructor = Mock(side_effect=AssertionError("provider must not be called"))
        fake_sdk = SimpleNamespace(SarvamAI=sarvam_constructor)
        with patch.dict(os.environ, {"SARVAM_API_KEY": ""}), \
                patch.object(app, "load_dotenv"), \
                patch.dict(sys.modules, {"sarvamai": fake_sdk}):
            status, _, _ = self.post_json({"notice": NOTICE, "language": "en"})

        self.assertEqual(status, 503)
        sarvam_constructor.assert_not_called()


if __name__ == "__main__":
    unittest.main()
