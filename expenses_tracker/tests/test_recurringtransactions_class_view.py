from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from expenses_tracker.models import Transaction
from expenses_tracker.views import RecurringTransactions


class RecurringTransactionsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_get_queryset(self):
        # Create sample data for testing
        transaction1 = Transaction.objects.create(
            user_id=self.user.id, recurring_transaction=True,
            frequency="monthly",
            category='Utility',
            amount=1000,
            description='This is the description'
        )
        transaction2 = Transaction.objects.create(
            user_id=self.user.id, recurring_transaction=True,
            frequency="weekly",
            category='Transportation',
            amount=200,
            description='This is the description'
        )

        # Set session data for filtering
        self.client.session['filter_category'] = 'Utility'
        self.client.session['sort_order'] = 'ascending'

        # Make GET request to the view
        response = self.client.get(reverse('recurring_transactions_page'))

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(str(transaction1.category), 'Utility')

        self.assertEqual(transaction2.amount, 200)

    def test_post(self):
        # Create sample data for testing
        transaction = Transaction.objects.create(
            user_id=self.user.id, recurring_transaction=True,
            frequency="weekly",
            # next_occurrence=timezone.now() + timedelta(weeks=1),
            category='Transportation',
            amount=100,
            description='This is the description'
        )

        # Make POST request to the view
        response = self.client.post(reverse('recurring_transactions_page'),
                                    {'recurring_transaction_id': transaction.id})

        # Check that the response status code is 302 (redirect)
        self.assertEqual(response.status_code, 302)

        # Check that the transaction object was updated as expected
        updated_transaction = Transaction.objects.get(id=transaction.id)
        self.assertFalse(updated_transaction.recurring_transaction)

        self.assertEqual(updated_transaction.transaction_title, None)

    def test_get_context_data(self):
        # Make GET request to the view
        response = self.client.get(reverse('recurring_transactions_page'))

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
