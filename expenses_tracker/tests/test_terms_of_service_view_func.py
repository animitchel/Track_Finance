from django.test import TestCase
from django.urls import reverse


class TermsOfServiceTestCase(TestCase):
    def test_terms_of_service(self):
        # Make a GET request to the terms of service view
        response = self.client.get(reverse('terms_of_service_page'))

        # Check if the correct template is rendered
        self.assertTemplateUsed(response, 'expenses_tracker/terms_of_service.html')

        # Check if the status code is 200
        self.assertEqual(response.status_code, 200)
