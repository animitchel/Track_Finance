from django.test import TestCase
from django.urls import reverse
from datetime import datetime
from unittest.mock import patch


class ContactUsViewTestCase(TestCase):
    def test_contact_us_get(self):
        # Make a GET request to the contact us view
        response = self.client.get(reverse('contact_us_page'))

        # Check if the correct template is rendered
        self.assertTemplateUsed(response, 'expenses_tracker/contact_us.html')

        # Check if the status code is 200
        self.assertEqual(response.status_code, 200)

    @patch('expenses_tracker.views.send_message')
    def test_contact_us_post(self, mock_send_message):
        # Prepare POST data
        post_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+12125552368',
            'message': 'Test message',
        }

        # Make a POST request to the contact us view
        response = self.client.post(reverse('contact_us_page'), data=post_data)

        # Print response content for debugging
        #print(response.content.decode('utf-8'))

        # Print any validation errors for debugging
        #print(response.context.get('form').errors)

        # Check if the message was sent
        mock_send_message.assert_called_once_with(
            'John Doe',
            'john@example.com',
            '+12125552368',
            'Test message'
        )

        # Check if the user is redirected after successful submission
        self.assertRedirects(response, reverse('contact_us_page'))
