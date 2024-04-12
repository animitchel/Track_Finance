from django.test import TestCase
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from unittest.mock import patch
from expenses_tracker.redirect_endpoints import url_has_allowed_host_and_scheme_func, allowed_endpoints


class RedirectValidationTestCase(TestCase):
    def setUp(self):
        self.allowed_hosts = allowed_endpoints
        self.valid_redirect_url = '/linechart/'
        self.invalid_redirect_url = 'https://malicious.com'

    def test_valid_redirect_url(self):
        result = url_has_allowed_host_and_scheme_func(
            self.valid_redirect_url,
            allowed_hosts=self.allowed_hosts
        )
        self.assertEqual(result, '/linechart/')

    def test_empty_redirect_url(self):
        result = url_has_allowed_host_and_scheme_func(
            '',
            allowed_hosts=self.allowed_hosts
        )
        self.assertIsNone(result)

    def test_non_string_redirect_url(self):
        result = url_has_allowed_host_and_scheme_func(
            None,
            allowed_hosts=self.allowed_hosts
        )
        self.assertIsNone(result)

    def test_injection_attempt(self):
        malicious_redirect_url = "https://example.com/';alert('XSS');'"
        result = url_has_allowed_host_and_scheme_func(
            malicious_redirect_url,
            allowed_hosts=self.allowed_hosts
        )
        self.assertIsNone(result)

    @patch('expenses_tracker.redirect_endpoints.url_has_allowed_host_and_scheme')
    def test_redirect_url_validity(self, mock_url_has_allowed_host_and_scheme):
        mock_url_has_allowed_host_and_scheme.return_value = True
        result = url_has_allowed_host_and_scheme_func(
            'https://example.com/invalid-url/',
            allowed_hosts=self.allowed_hosts
        )
        self.assertIsNone(result)

    @patch('expenses_tracker.redirect_endpoints.url_has_allowed_host_and_scheme')
    def test_redirect_url_invalidity(self, mock_url_has_allowed_host_and_scheme):
        mock_url_has_allowed_host_and_scheme.return_value = False
        result = url_has_allowed_host_and_scheme_func(
            'https://example.com/valid-url/',
            allowed_hosts=self.allowed_hosts
        )
        self.assertIsNone(result)
