from django.utils.http import url_has_allowed_host_and_scheme
from urllib.parse import urlparse

allowed_endpoints = ["/linechart/", "/account-settings/", "/notifications/", "/profile-details/",
                     "/expense-reports-form/", "/income-category/", "/add-income/", "/expenses-report/", "/add-budget/",
                     "/budget-overview/", "/recurring-incomes/", "/recurring-transactions/", "/categories/",
                     "/add_transactions/", "/all_transactions/", "/overview/", "/logout/", "/income-data/",
                     "/barchart/", "/exchange-rate/", "/transaction-update/<int:pk>/",
                     ]


def url_has_allowed_host_and_scheme_func(redirect, allowed_hosts, scheme=None):
    """
    Check if the redirect URL has allowed host and scheme, and matches an allowed endpoint.

    Args:
        redirect (str): The URL to be checked.
        allowed_hosts (list): List of allowed hosts.
        scheme (str): Optional. The scheme to check against.

    Returns:
        str or None: The matched endpoint if the URL is valid and matches an allowed endpoint, else None.
    """
    # Validate redirect URL
    if not redirect:
        return None  # Return None for empty redirect URL

    if not isinstance(redirect, str):
        return None  # Reject non-string input

    # Check for injection attempts or unexpected input
    if any(char in redirect for char in [';', "'", '"', '<', '>', '(', ')', '|', '`']):
        return None  # Reject input containing suspicious characters

    # Check if the redirect URL has allowed host and scheme
    if url_has_allowed_host_and_scheme(redirect, allowed_hosts=allowed_hosts):

        # Check if the path of the redirect URL matches any allowed endpoint
        valid_endpoint = next((url for url in allowed_endpoints if urlparse(redirect).path == url), None)
        return valid_endpoint
