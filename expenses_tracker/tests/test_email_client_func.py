from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
import os


class SendMessageTestCase(TestCase):
    @patch('expenses_tracker.email_client.smtplib.SMTP')
    def test_send_message(self, mock_smtp):

        # Define test data
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

        # Assertions
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with(
            user=os.getenv('EMAIL_USER_FROM'),
            password=os.getenv('PASSWORD')
        )
        mock_smtp_instance.send_message.assert_called_once()

        sent_message = mock_smtp_instance.send_message.call_args[0][0]
        self.assertEqual(sent_message['From'], os.getenv('EMAIL_USER_FROM'))
        self.assertEqual(sent_message['To'], os.getenv('EMAIL_USER_TO'))
        self.assertEqual(sent_message['Subject'], 'Track-Finance')
        self.assertIn('Name: John Doe', sent_message.get_payload())
        self.assertIn('Email: john@example.com', sent_message.get_payload())
        self.assertIn('Phone: +12125552368', sent_message.get_payload())
        self.assertIn('Message: Test message', sent_message.get_payload())

        # Check if the user is redirected after successful submission
        self.assertRedirects(response, reverse('contact_us_page'))

