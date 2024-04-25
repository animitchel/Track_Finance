from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from expenses_tracker.models import Income
from django.core.cache import cache


class IncomeCategoryViewTestCase(TestCase):
    def setUp(self):
        cache.clear()
        # Create a test client
        self.client = Client()

        # Create a user for testing
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_get_request(self):
        # Log in the user
        self.client.force_login(self.user)

        # Create test income records with different categories
        income1 = Income.objects.create(user=self.user, category='Category1', amount=100, date=timezone.now())
        income2 = Income.objects.create(user=self.user, category='Category2', amount=200, date=timezone.now())

        # Make a GET request to the view
        response = self.client.get(reverse('income_category_page'))

        # Check the response status code
        self.assertEqual(response.status_code, 200)

        # Check if the categories are present in the context
        self.assertIn('Category1', response.context['categories'])
        self.assertIn('Category2', response.context['categories'])

