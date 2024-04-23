from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import datetime, timedelta
from expenses_tracker.models import Income


class RecurringIncomesTestCase(TestCase):
    def setUp(self):
        # Create a test client
        self.client = Client()

        # Create a user for testing
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_get_request(self):
        # Log in the user
        self.client.force_login(self.user)

        # Create a test recurring income record
        Income.objects.create(
            user=self.user, recurring_transaction=True,
            frequency='weekly', category='rental income', amount=1000, notes='test notes'
        )

        # Make a GET request to the view
        response = self.client.get(reverse('recurring_income_page'))

        # Check the response status code
        self.assertEqual(response.status_code, 200)

        # Check if the recurring income is present in the context
        self.assertTrue(response.context['recurring_transactions_incomes'])

    def test_post_request(self):
        # Log in the user
        self.client.force_login(self.user)

        # Create a test recurring income record
        income = Income.objects.create(user=self.user, recurring_transaction=True,
                                       frequency='weekly', category='rental income', amount=1000, notes='test notes')

        # Make a POST request to the view to delete the recurring income record
        response = self.client.post(reverse('recurring_income_page'), {'recurring_transaction_id': income.id})

        # Check the response status code
        self.assertEqual(response.status_code, 302)  # Expecting a redirect after deletion

        income.refresh_from_db()

        # Check if the recurring income record is deleted
        self.assertEqual(income.recurring_transaction, False)
