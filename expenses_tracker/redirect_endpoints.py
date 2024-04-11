from django.utils.http import url_has_allowed_host_and_scheme

allowed_endpoints = ["/linechart/", "/account-settings/", "/notifications/", "/profile-details/",
                     "/expense-reports-form/", "/income-category/", "/add-income/", "/expenses-report/", "/add-budget/",
                     "/budget-overview/", "/recurring-incomes/", "/recurring-transactions/", "/categories/",
                     "/add_transactions/", "/all_transactions/", "/overview/", "/logout/", "/income-data/"]


def url_has_allowed_host_and_scheme_func(redirect, allowed_hosts, scheme=None):
    # Validate redirect URL
    if not redirect:
        return None  # Return None for empty redirect URL

    if not isinstance(redirect, str):
        return None  # Reject non-string input

    # Check for injection attempts or unexpected input
    if any(char in redirect for char in [';', "'", '"', '<', '>', '(', ')', '|', '`']):
        return None  # Reject input containing suspicious characters

    if url_has_allowed_host_and_scheme(redirect, allowed_hosts=allowed_hosts):

        valid_endpoint = next((url for url in allowed_endpoints if redirect == url), None)
        return valid_endpoint
