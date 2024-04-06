from django.test import TestCase, RequestFactory, Client
from django.contrib.auth.models import AnonymousUser, User
from django.urls import reverse
from expenses_tracker.views import IndexView


class IndexViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_view_rendering(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'expenses_tracker/index.html')

    def test_index_view_context_data_authenticated_user(self):
        user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        self.client.force_login(user)
        response = self.client.get(reverse('home'))
        self.assertTrue(response.context['user_status'])
        self.assertEqual(response.context['current_year'], response.context['current_year'])

    def test_index_view_context_data_anonymous_user(self):
        response = self.client.get(reverse('home'))
        self.assertFalse(response.context['user_status'])
        self.assertEqual(response.context['current_year'], response.context['current_year'])

    def test_index_view_context_data_custom_year(self):
        custom_year = 2023
        response = self.client.get(reverse('home'))
        self.assertEqual(response.context['current_year'], response.context['current_year'])
        self.assertNotEqual(response.context['current_year'], custom_year)





