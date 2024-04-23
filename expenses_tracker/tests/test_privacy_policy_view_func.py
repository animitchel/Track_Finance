from django.test import TestCase
from django.urls import reverse


class PrivacyPolicyTestCase(TestCase):
    def test_privacy_policy(self):
        # Make a GET request to the privacy policy view
        response = self.client.get(reverse('privacy_policy_page'))

        # Check if the correct template is rendered
        self.assertTemplateUsed(response, 'expenses_tracker/privacy_policy.html')

        # Check if the status code is 200
        self.assertEqual(response.status_code, 200)
