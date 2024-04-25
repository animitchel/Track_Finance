from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum, aggregates
from expenses_tracker.models import Transaction, Budget, Income
from django.core.cache import cache


class OverviewViewTest(TestCase):
    def setUp(self):
        cache.clear()
        self.client = Client()
        self.user = User.objects.create_user(username='test_user', email='test@example.com', password='test_password')

    def test_overview_view_authenticated_user(self):
        self.client.login(username='test_user', password='test_password')

        # Create sample transactions
        transaction1 = Transaction.objects.create(category='Groceries', amount=50.0, user=self.user)
        transaction2 = Transaction.objects.create(category='Utilities', amount=100.0, user=self.user)
        transaction3 = Transaction.objects.create(category='Transportation', amount=75.0, user=self.user)

        # Create sample budgets
        budget1 = Budget.objects.create(category='Food', budget=200.0, amount=150.0, user=self.user, duration='1 week')
        budget2 = Budget.objects.create(
            category='Entertainment', budget=100.0, amount=50.0, user=self.user, duration='2 weeks'
        )

        # Create sample income data
        income1 = Income.objects.create(category='Salary', amount=3000.0, user=self.user)
        income2 = Income.objects.create(category='Investment', amount=500.0, user=self.user)

        transactions = Transaction.objects.all()
        category_transactions = transactions.order_by('-date')[:3]

        category = {field.category: transactions.filter(category=field.category).aggregate(
            sum=Sum('amount')).get('sum') for field in category_transactions}

        # Make a GET request to the overview view
        response = self.client.get(reverse('overview_page'))

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        self.assertEqual(type(category), dict)
        self.assertEqual(len(category), 3)

        for field in transactions:
            self.assertEqual(field.amount, category[field.category])

        # Check that the rendered template is correct
        self.assertTemplateUsed(response, 'expenses_tracker/overview.html')
        self.assertContains(response, 'Food')
        self.assertContains(response, 'Groceries')
        self.assertContains(response, 'Salary')

    def test_overview_view_unauthenticated_user(self):
        # Make a GET request to the overview view without logging in
        response = self.client.get(reverse('overview_page'))

        # Check that the response redirects to the login page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/overview/')
