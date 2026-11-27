import http.cookiejar
import io
import json
import os
import sys
import unittest
import urllib.request
from unittest.mock import Mock, patch
from urllib.error import HTTPError
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "cli_scripts"))
import jenkins_api


class Input:
    def __init__(self, data):
        self.buffer = io.BytesIO(data)


class Response:
    def __init__(self, data=b"", headers=None):
        self.data = data
        self.headers = headers or {}

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self.data


class JenkinsApiTests(unittest.TestCase):
    def setUp(self):
        self.url = patch.object(jenkins_api, "BASE_URL", "http://jenkins.test/jenkins")
        self.identity = patch.object(jenkins_api, "IDENTITY", "service-user")
        self.url.start()
        self.identity.start()
        self.addCleanup(self.url.stop)
        self.addCleanup(self.identity.stop)

    @patch("urllib.request.urlopen")
    def test_lists_jobs_using_service_identity(self, urlopen):
        urlopen.return_value = Response(b'{"jobs":[{"name":"zeta"},{"name":"alpha"}]}')
        output = io.StringIO()
        with patch("sys.stdout", output):
            self.assertEqual(jenkins_api.main(["jobs", "ls"]), 0)
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "http://jenkins.test/jenkins/api/json?tree=jobs[name]")
        self.assertEqual(request.get_header("X-forwarded-user"), "service-user")
        self.assertEqual(output.getvalue(), "alpha\nzeta\n")

    @patch("urllib.request.build_opener")
    def test_create_fetches_crumb_and_posts_xml_in_cookie_session(self, build_opener):
        opener = Mock()
        opener.open.side_effect = [
            Response(b'{"crumbRequestField":"Jenkins-Crumb","crumb":"crumb-value"}'),
            Response(),
        ]
        build_opener.return_value = opener
        with patch("sys.stdin", Input(b"<project/>")):
            self.assertEqual(jenkins_api.main(["jobs", "create", "lab & test"]), 0)
        crumb_request, create_request = [call.args[0] for call in opener.open.call_args_list]
        cookie_processor = build_opener.call_args.args[0]
        self.assertIsInstance(cookie_processor, urllib.request.HTTPCookieProcessor)
        self.assertIsInstance(cookie_processor.cookiejar, http.cookiejar.CookieJar)
        self.assertEqual(crumb_request.full_url, "http://jenkins.test/jenkins/crumbIssuer/api/json")
        self.assertEqual(crumb_request.get_header("X-forwarded-user"), "service-user")
        self.assertEqual(create_request.method, "POST")
        self.assertIn("name=lab+%26+test", create_request.full_url)
        self.assertEqual(create_request.get_header("Jenkins-crumb"), "crumb-value")
        self.assertEqual(create_request.get_header("Content-type"), "application/xml")
        self.assertEqual(create_request.data, b"<project/>")

    @patch("urllib.request.build_opener")
    def test_job_mutation_encodes_job_path_and_sends_crumb(self, build_opener):
        opener = Mock()
        opener.open.side_effect = [
            Response(b'{"crumbRequestField":"Jenkins-Crumb","crumb":"c"}'),
            Response(),
        ]
        build_opener.return_value = opener
        self.assertEqual(jenkins_api.main(["jobs", "disable", "folder/job one"]), 0)
        request = opener.open.call_args_list[1].args[0]
        self.assertEqual(
            request.full_url,
            "http://jenkins.test/jenkins/job/folder/job/job%20one/disable",
        )
        self.assertEqual(request.get_header("Jenkins-crumb"), "c")

    @patch("urllib.request.urlopen")
    def test_http_errors_are_reported_with_nonzero_status(self, urlopen):
        urlopen.side_effect = HTTPError(
            "http://jenkins.test/jenkins/api/json",
            403,
            "Forbidden",
            {},
            io.BytesIO(b"denied"),
        )
        error = io.StringIO()
        with patch("sys.stderr", error):
            self.assertEqual(jenkins_api.main(["jobs", "ls"]), 1)
        self.assertIn("HTTP 403 Forbidden: denied", error.getvalue())


if __name__ == "__main__":
    unittest.main()
