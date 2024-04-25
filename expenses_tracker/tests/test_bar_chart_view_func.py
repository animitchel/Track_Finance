from django.test import TestCase, Client
from django.contrib.auth.models import User
from expenses_tracker.views import bar_chart
from  django.urls import reverse
from django.core.cache import cache


class BarChartTestCase(TestCase):
    def setUp(self):
        # Create a test user
        cache.clear()
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_bar_chart_view(self):
        # Create a client to simulate HTTP requests
        client = Client()

        # Log in the test user
        client.login(username='testuser', password='password')

        # Make a GET request to the bar_chart view
        response = client.get(reverse('bar_chart_page'))

        # Check if the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Perform assertions on the response content
        self.assertContains(response, 'Bar Chart')
        self.assertContains(response, 'Transactions Categories')
        self.assertContains(response, 'Incomes Sources')

