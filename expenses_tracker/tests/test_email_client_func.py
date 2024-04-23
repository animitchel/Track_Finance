from django.test import TestCase
from django.urls import reverse
from datetime import datetime
from unittest.mock import patch, MagicMock, ANY
from expenses_tracker.views import send_message
import smtplib
import os


class ContactUsViewTestCase(TestCase):
    @patch('expenses_tracker.email_client.smtplib.SMTP')
    def test_contact_us_post(self, mock_smtp):
        # Prepare POST data
        post_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+12125552368',
            'message': 'Test message',
        }

        # Make a POST request to the contact us view
        response = self.client.post(reverse('contact_us_page'), data=post_data)

        # Check if the message was sent
        mock_smtp_instance = mock_smtp.return_value.__enter__.return_value

        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with(user=os.getenv("EMAIL_USER_FROM"), password=os.getenv("PASSWORD"))
        mock_smtp_instance.sendmail.assert_called_once_with(
            from_addr=os.getenv('EMAIL_USER_FROM'),
            to_addrs=os.getenv('EMAIL_USER_TO'),
            msg=ANY  # We use ANY to ensure that any message is passed to sendmail
        )

        # Check if the user is redirected after successful submission
        self.assertRedirects(response, reverse('contact_us_page'))
