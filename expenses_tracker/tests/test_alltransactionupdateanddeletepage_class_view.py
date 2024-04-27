from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from expenses_tracker.models import Transaction, Budget
from django.utils import timezone


class AllTransactionUpdateAndDeletePageTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.test_user = User.objects.create_user(username='test_user', password='test_password')

        # Create a test budget
        self.budget = Budget.objects.create(
            user=self.test_user, category='Groceries', amount=500,
            description="Test Description", duration='2 weeks',
        )

        # Create a test transaction
        self.transaction = Transaction.objects.create(user=self.test_user, amount=100, date=timezone.now())

    def test_update_page(self):
        # Create a test client
        client = Client()

        # Login as test user
        client.login(username='test_user', password='test_password')

        # Get the URL for the update page
        url = reverse('transaction_update', kwargs={'pk': self.transaction.pk})

        # Make a GET request to the update page
        response = client.get(url)

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the template used is correct
        self.assertTemplateUsed(response, 'expenses_tracker/add_transaction.html')

        # Check if the context contains necessary data
        self.assertTrue(response.context['update'])
        self.assertTrue(response.context['user_status'])
        self.assertEqual(response.context['current_year'], timezone.now().year)
        self.assertEqual(response.context['object'], self.transaction.id)
        self.assertEqual(response.context['header_name'], 'Update Transaction')

    def test_form_valid(self):
        # Create a test client
        client = Client()

        # Login as test user
        client.login(username='test_user', password='test_password')

        # Get the URL for the update page
        url = reverse('transaction_update', kwargs={'pk': self.transaction.pk})

        form_data = {
            'category': 'Education',
            'amount': 200.0,
            'description': 'Test Description',
            'recurring_transaction': True,
            'frequency': 'monthly',
            'transaction_title': 'Test Transaction'
        }

        # Make a POST request to the update page
        response = client.post(url, form_data, follow=True)

        self.assertEqual(response.status_code, 200)

        # Check if the transaction has been updated
        updated_transaction = Transaction.objects.get(pk=self.transaction.pk)
        self.assertEqual(updated_transaction.amount, 200)

        # # Check if the budget has been updated
        # updated_budget = Budget.objects.get(pk=self.budget.pk)
        # self.assertEqual(updated_budget.amount, 300)  # 500 - 200 = 300
