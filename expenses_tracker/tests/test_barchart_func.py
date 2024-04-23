from django.test import TestCase, Client
from django.test.client import RequestFactory
from django.contrib.auth.models import User
from expenses_tracker.views import barchart
from django.urls import reverse


class BarChartTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

    def test_barchart_generation(self):
        # Create a queryset (you can replace this with actual data as needed)
        object_inst = {'Travel': 100, 'Taxes': 200, 'Food': 150}

        # Create a client to simulate HTTP requests
        client = Client()
        client.login(username='testuser', password='password')

        # Generate a response by making a request to a dummy URL
        response = client.get('/')
        response.session = client.session
        response.session['user_currency'] = '$'

        # Generate the bar chart
        chart = barchart(object_inst, response, 'Transactions Categories')

        # Perform assertions on the generated chart HTML
        self.assertIn('Transactions Categories', chart)
        self.assertIn('Travel', chart)
        self.assertIn('Taxes', chart)
        self.assertIn('Food', chart)
        self.assertIn('100', chart)  # Ensure data from object_inst is present in the chart
