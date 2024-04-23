from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from expenses_tracker.models import Profile


class LoginUserTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.profile = Profile.objects.create(user=self.user, currency='$')

    def test_login_successful_redirect(self):
        data = {
            'username': 'testuser',
            'password': 'password123',
        }

        response = self.client.post(reverse('login_page'), data, follow=True)
        self.assertRedirects(response, reverse('home'))
        self.assertIn('user_currency', self.client.session)
        self.assertIn('current_user', self.client.session)
        self.assertEqual(self.client.session['current_user'], self.user.id)

    def test_login_unsuccessful(self):
        data = {
            'username': 'testuser',
            'password': 'wrongpassword',
        }
        response = self.client.post(reverse('login_page'), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('error_message', response.context)
        self.assertIn('Username or password is incorrect', response.context['error_message'])
