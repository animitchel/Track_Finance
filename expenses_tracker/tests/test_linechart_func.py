from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client
from expenses_tracker.models import Transaction
from expenses_tracker.graphical_insights import linechart
# from datetime import datetime
from django.core.cache import cache
from django.urls import reverse


class LineChartTestCase(TestCase):
    def setUp(self):
        cache.clear()
        # Create a test user
        self.test_user = User.objects.create_user(username='test_user', password='test_password')

        # Create test transactions
        self.transaction1 = Transaction.objects.create(user=self.test_user, amount=100)
        self.transaction2 = Transaction.objects.create(user=self.test_user, amount=200)

    def test_linechart_generation(self):
        # Create a test client
        client = Client()

        # Login as test user
        client.login(username='test_user', password='test_password')

        # Get object_inst (transactions)
        transactions = Transaction.objects.filter(user=self.test_user)

        # Make a request to the view that generates the line chart
        response = client.get(reverse('line_chart_page'))

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the chart HTML contains expected elements
        self.assertIn('lines+markers', response.content.decode('utf-8'))
        self.assertIn('Date', response.content.decode('utf-8'))
        self.assertIn('Amount', response.content.decode('utf-8'))

    # Add more test cases as needed
