from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from expenses_tracker.models import Profile
from datetime import datetime
from django.http import HttpResponseRedirect


class AccountSettingsViewTestCase(TestCase):
    def setUp(self):
        # Create a test client
        self.client = Client()

        # Create a user for testing
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        # Log in the user
        self.client.login(username='testuser', password='testpassword')

        profile = Profile.objects.create(user=self.user, currency='USD')

    def test_get_request(self):
        # Make a GET request to the view
        response = self.client.get(reverse('account_settings_page'))

        # Check the response status code
        self.assertEqual(response.status_code, 200)

        # Check if the form is present in the context
        self.assertIn('form', response.context)

    def test_post_valid_form(self):
        # Create a profile for the user
        # profile = Profile.objects.create(user=self.user, currency='USD')

        # Data to update profile
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'occupation': 'Software Engineer',
            'city': 'New York',
            'country': 'USA',
            'phone_number': '+999999999',
        }

        # Make a POST request with valid form data
        response = self.client.post(reverse('account_settings_page'), data)

        # Check the response status code
        self.assertEqual(response.status_code, 200)

        # Check if the profile was updated successfully
        updated_profile = Profile.objects.get(user=self.user)
        self.assertEqual(updated_profile.currency, 'USD')

    def test_post_invalid_form(self):
        # Make a POST request with invalid form data
        response = self.client.post(reverse('account_settings_page'), {})

        # Check the response status code
        self.assertEqual(response.status_code, 200)  # Expecting to redirect to the same page

        # Check if the form errors are present in the context
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)
