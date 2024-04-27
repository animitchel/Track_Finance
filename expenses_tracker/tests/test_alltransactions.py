from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from expenses_tracker.models import Transaction, Budget
from django.db.models import Sum, aggregates


class AllTransactionsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test_user', email='test@example.com', password='test_password')

    def test_get_queryset_with_filter_category(self):
        self.client.login(username='test_user', password='test_password')

        # Create sample transactions
        Transaction.objects.create(
            category='Groceries', amount=50.0, user=self.user, description='test description')
        Transaction.objects.create(category='Utilities', amount=100.0, user=self.user)

        # Make a GET request to the view
        response = self.client.get(reverse('all_transactions_page'))

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

    # def test_post_method_with_transaction_id(self):
    #     self.client.login(username='test_user', password='test_password')
    #
    #     # Create a sample transaction
    #     transaction = Transaction.objects.create(category='Groceries', amount=50.0, user=self.user)
    #     Transaction.objects.create(category='Groceries', amount=60.0, user=self.user)
    #
    #     # Make a POST request to the view with transaction_id
    #     response = self.client.post(reverse('all_transactions_page'), {'all_transaction_id': transaction.id})
    #
    #     # Check that the response is a redirect
    #     self.assertEqual(response.status_code, 302)
    #
    #     # Check that transaction was successfully deleted
    #     self.assertNotIn(transaction, Transaction.objects.all())

    def test_post_method_with_search_query(self):
        # Create sample transactions
        Transaction.objects.create(
            category='Groceries', amount=50.0, user=self.user, description='test description')

        Transaction.objects.create(category='Utilities', amount=100.0, user=self.user)

        Transaction.objects.create(
            category='Utilities', amount=100.0, user=self.user, description='test description')

        self.client.login(username='test_user', password='test_password')

        # Set session data for search query
        session = self.client.session
        session['search_query'] = 'test'
        session.save()

        # Make a POST request to the view with search query
        response = self.client.post(reverse('all_transactions_page'), {'search': 'test'})

        # Check that the response is a redirect
        self.assertEqual(response.status_code, 302)

        # Access the Location header to get the redirect URL
        redirect_url = response.url

        # Follow the redirect by making another request
        redirected_response = self.client.get(redirect_url)

        self.assertContains(redirected_response, session['search_query'], 2)
