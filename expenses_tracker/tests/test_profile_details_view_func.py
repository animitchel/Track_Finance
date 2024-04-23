from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import datetime
from expenses_tracker.models import Profile


class ProfileDetailsTestCase(TestCase):
    def setUp(self):
        # Create a test client
        self.client = Client()

        # Create a user for testing
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_get_request(self):
        # Log in the user
        self.client.force_login(self.user)

        # Create a profile for the user
        profile = Profile.objects.create(user=self.user)

        # Make a GET request to the view
        response = self.client.get(reverse('profile_page'))

        # Check the response status code
        self.assertEqual(response.status_code, 200)

        # Check if the profile is present in the context
        self.assertEqual(response.context['profile'], profile)

    def test_missing_profile_image(self):
        # Log in the user
        self.client.force_login(self.user)

        # Create a profile for the user without an image
        profile = Profile.objects.create(user=self.user)

        # Make a GET request to the view
        response = self.client.get(reverse('profile_page'))

        # Check if the default image path is set for the profile
        self.assertEqual(response.context['profile'].image, 'images/c0749b7cc401421662ae901ec8f9f660.jpg')
