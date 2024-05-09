from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import datetime, timedelta
from django.utils import timezone
from expenses_tracker.models import Transaction, Income, Budget
from django.core.cache import cache


class NotificationTestCase(TestCase):
    def setUp(self):
        cache.clear()
        # Create a test client
        self.client = Client()

        # Create a user for testing
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_get_request(self):
        # Log in the user
        self.client.force_login(self.user)

        # Create some test instances due in the next 24 hours
        current_datetime = timezone.now()
        next_24_hours = current_datetime + timedelta(hours=24)

        transaction_instance = Transaction.objects.create(
            category='Groceries',
            amount=30.00,
            description='Test Description',
            recurring_transaction=True,
            frequency='weekly',
            transaction_title='Test Transaction',
            user=self.user,
            date=current_datetime - timedelta(days=6)
        )
        income_instance = Income.objects.create(
            amount=100,
            category='business income',
            notes='Test notes for testing',
            recurring_transaction=True,
            frequency='weekly',
            transaction_title='Test Transaction',
            user=self.user,
            date=current_datetime - timedelta(days=6)
        )
        budget_instance = Budget.objects.create(
            category='Groceries',
            amount='500.00',
            description='Monthly groceries budget',
            duration='1 week',
            user=self.user,
            date=current_datetime - timedelta(days=6)
        )

        # Make a GET request to the view
        response = self.client.get(reverse('notification_page'))

        # Check the response status code
        self.assertEqual(response.status_code, 200)

        # Check if instances due in the next 24 hours are present in the context
        # self.assertIn(transaction_instance, response.context['transactions_instances_next_24_hours'])
        # self.assertIn(income_instance, response.context['incomes_instances_next_24_hours'])
        self.assertIn(budget_instance, response.context['budgets_instances_next_24_hours'])

    def test_no_instances_due(self):
        # Log in the user
        self.client.force_login(self.user)

        # Make a GET request to the view
        response = self.client.get(reverse('notification_page'))

        # Check the response status code
        self.assertEqual(response.status_code, 200)

        # Check if there are no instances due in the next 24 hours
        self.assertQuerysetEqual(response.context['transactions_instances_next_24_hours'], [])
        self.assertQuerysetEqual(response.context['incomes_instances_next_24_hours'], [])
        self.assertQuerysetEqual(response.context['budgets_instances_next_24_hours'], [])
