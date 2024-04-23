from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class RegisterViewTestCase(TestCase):
    def test_get(self):
        # Make a GET request to the register page
        response = self.client.get(reverse('register_page'))

        # Check if the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Check if the necessary forms are present in the context
        self.assertIn('form', response.context)
        self.assertIn('user_form', response.context)

        # Check if the user is not authenticated
        self.assertFalse(response.context['user_status'])

        # Check if the 'Currency' field is present
        self.assertIn('Currency', response.context['fields_to_display'])

    def test_post_valid_form(self):
        # Data for a valid user and profile form submission
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword',
            'confirm_password': 'testpassword',
            'currency': '$'
            # Include other required fields for profile form
        }

        # Make a POST request with valid form data
        response = self.client.post(reverse('register_page'), data, follow=True)

        # Check if the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Check if the user is redirected to the login page
        self.assertRedirects(response, reverse('login_page'))

        # Check if the login message is present in the session
        self.assertNotIn("login_msg", self.client.session)

        # Check if the user is created
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_post_invalid_form(self):
        # Data for an invalid user and profile form submission
        invalid_data = {
            # Include incomplete or invalid form data
        }

        # Make a POST request with invalid form data
        response = self.client.post(reverse('register_page'), invalid_data)

        # Check if the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Check if the necessary forms are present in the context
        self.assertIn('form', response.context)
        self.assertIn('user_form', response.context)

        # Check if the user is not authenticated
        self.assertFalse(response.context['user_status'])

        # Check if the 'Currency' field is present
        self.assertIn('Currency', response.context['fields_to_display'])
