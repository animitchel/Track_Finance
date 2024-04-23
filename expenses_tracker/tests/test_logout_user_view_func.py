from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class LogoutUserTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_logout_user(self):
        # Log in the user
        self.client.login(username='testuser', password='password123')

        # Make a GET request to the logout view
        response = self.client.get(reverse('logout'))

        # Check if the user is redirected to the login page
        self.assertRedirects(response, reverse('login_page'))

        # Check if the session is empty
        self.assertEqual(len(self.client.session.keys()), 0)
