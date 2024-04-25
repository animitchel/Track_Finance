from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from expenses_tracker.models import Transaction, Income
from expenses_tracker.form_models import DateForm
from unittest.mock import patch
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.views.decorators.cache import cache_page, never_cache
from django.core.cache import cache


class LineChartViewTestCase(TestCase):

    def setUp(self):
        cache.clear()

    @classmethod
    def setUpTestData(cls):
        # Create test user
        cls.test_user = User.objects.create_user(username='testuser', password='12345678901')

        # Create test transactions
        cls.start_date = timezone.now().date() - timedelta(days=7)
        cls.end_date = timezone.now().date()
        cls.transaction1 = Transaction.objects.create(
            user=cls.test_user, amount=100, category='Housing',
            description='This is a test transaction'
        )
        cls.transaction2 = Transaction.objects.create(
            user=cls.test_user, amount=200,
            category='Food',
            description='This is a test transaction'
        )

        # Create test incomes
        cls.income1 = Income.objects.create(user=cls.test_user, amount=300,
                                            category='Housing',
                                            notes='This is a test transaction'
                                            )
        cls.income2 = Income.objects.create(
            user=cls.test_user, amount=400,
            category='salary or wages',
            notes='This is a test transaction'
        )

    def test_authenticated_user_with_valid_form(self):
        self.client.force_login(self.test_user)
        response = self.client.post(reverse('line_chart_page'), data={'start': self.start_date, 'end': self.end_date})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('chart' in response.context)
        self.assertTrue('chart2' in response.context)
        self.assertTrue('form' in response.context)
        self.assertTrue(response.context['user_status'])
        self.assertIsInstance(response.context['form'], DateForm)

    def test_authenticated_user_with_invalid_form(self):
        self.client.force_login(self.test_user)
        response = self.client.post(reverse('line_chart_page'), data={})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('chart' in response.context)
        self.assertTrue('chart2' in response.context)
        self.assertTrue('form' in response.context)
        self.assertTrue(response.context['user_status'])
        self.assertIsInstance(response.context['form'], DateForm)
        self.assertTrue(response.context['user_status'])

    def test_authenticated_user_without_form_submission(self):
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('line_chart_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('chart' in response.context)
        self.assertTrue('chart2' in response.context)
        self.assertTrue('form' in response.context)
        self.assertTrue(response.context['user_status'])
        self.assertIsInstance(response.context['form'], DateForm)

    def test_unauthenticated_user(self):
        response = self.client.get(reverse('line_chart_page'))
        self.assertEqual(response.status_code, 302)  # Redirects to login page

    @patch('expenses_tracker.views.linechart')
    def test_toggle_income_visualization(self, mock_linechart):
        # Create a request factory instance
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('line_chart_page'), data={'start': self.start_date, 'end': self.end_date,
                                                                      'toggle_state': 'True'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_linechart.called)
