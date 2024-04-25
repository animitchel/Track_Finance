from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.timezone import datetime
from django.db.models import Sum
from expenses_tracker.models import Transaction  # Import your Transaction model
from expenses_tracker.views import CategoryView
from django.core.cache import cache


class CategoryViewTestCase(TestCase):

    def setUp(self):
        cache.clear()

    @classmethod
    def setUpTestData(cls):
        # Create a user for testing
        cls.user = User.objects.create_user(username='testuser', password='12345')

    def test_get_queryset(self):
        # Create sample transactions for the user
        transaction1 = Transaction.objects.create(user=self.user, category='Category1', amount=100)
        transaction2 = Transaction.objects.create(user=self.user, category='Category1', amount=200)
        transaction3 = Transaction.objects.create(user=self.user, category='Category2', amount=300)

        # Log in as the test user
        self.client.login(username='testuser', password='12345')

        # Get the response from the view
        response = self.client.get(reverse('categories_page'))

        # Check the response status code
        self.assertEqual(response.status_code, 200)

        # Check the context object name
        self.assertIn('categories', response.context)

        # Check the categories in the context
        categories = response.context['categories']
        self.assertEqual(categories['Category1'], 300)  # Total amount for Category1
        self.assertEqual(categories['Category2'], 300)  # Total amount for Category2

    def test_get_context_data(self):
        # Log in as the test user
        self.client.login(username='testuser', password='12345')

        # Get the response from the view
        response = self.client.get(reverse('categories_page'))

        # Check the response status code
        self.assertEqual(response.status_code, 200)

        # Check the context data
        self.assertIn('user_currency', response.context)
        self.assertIn('user_status', response.context)
        self.assertIn('current_year', response.context)
