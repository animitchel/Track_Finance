from django.test import TestCase, Client
from django.urls import reverse
from datetime import datetime
from django.contrib.auth.models import User
from expenses_tracker.models import Transaction, Budget
from expenses_tracker.views import AddTransactionView, budget_calc


# from expenses_tracker.forms import TransactionForm


class AddTransactionViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_add_transaction_view(self):
        # Log in the user
        self.client.login(username='testuser', password='12345')

        # Create a budget object for the user
        budget = Budget.objects.create(
            user=self.user, category='Groceries', budget=100.0, amount=50.0, duration='2 weeks')

        # Prepare form data
        form_data = {
            'category': 'Groceries',
            'amount': 30.0,
            'description': 'Test Description',
            'recurring_transaction': True,
            'frequency': 'monthly',
            'transaction_title': 'Test Transaction'
        }

        # Send POST request to the view
        response = self.client.post(reverse('add_transactions_page'), form_data, follow=True)

        # Check if the form submission was successful and to the correct URL
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'expenses_tracker/all_transactions.html')

        # Confirm the URL the response is redirected to
        self.assertEqual(response.request['PATH_INFO'], reverse('all_transactions_page'))

        self.assertContains(response, 'Test Description', count=1)

        # Check if the budget was updated correctly
        budget.refresh_from_db()
        self.assertEqual(budget.amount, 20.0)
        self.assertEqual(budget.spent, 80.0)

        # Check if the transaction was added to the database
        self.assertTrue(Transaction.objects.filter(category='Groceries', amount=30.0).exists())

    def test_budget_calc_function(self):
        # Create a budget object
        budget = Budget.objects.create(user=self.user, category='Groceries', budget=100.0, amount=50.0,
                                       duration='1 week')
        budget2 = Budget.objects.create(
            user=self.user, category='All Transactions', budget=100.0, amount=50.0, duration='2 weeks',
        )

        # Create a form instance with amount=30.0
        form_instance = Transaction(amount=30.0, is_all_trans_bud=True, category='Groceries')

        # Call the budget_calc function
        budget_calc(budget, form_instance)
        # for All Transactions
        budget_calc(budget2, form_instance)

        # Check if the budget was updated correctly
        budget.refresh_from_db()
        self.assertEqual(budget.amount, 20.0)
        self.assertEqual(budget.spent, 80.0)

        # for All Transactions budget
        budget2.refresh_from_db()
        self.assertEqual(budget2.amount, 20.0)
        self.assertEqual(budget2.spent, 80.0)
