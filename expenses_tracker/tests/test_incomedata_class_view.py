from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import datetime
from django.utils import timezone
from expenses_tracker.models import Income
from expenses_tracker.views import IncomeData


class IncomeDataTestCase(TestCase):
    def setUp(self):
        # Create a test client
        self.client = Client()

        # Create a user for testing
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_get_request(self):
        # Log in the user
        self.client.force_login(self.user)

        # Make a GET request to the view
        response = self.client.get(reverse('income_data_page'))

        # Check the response status code
        self.assertEqual(response.status_code, 200)

    def test_post_request_delete_income(self):
        # Log in the user
        self.client.force_login(self.user)

        # Create a test income record
        income = Income.objects.create(user=self.user, amount=100, date=timezone.now())

        # Make a POST request to delete the income record
        response = self.client.post(reverse('income_data_page'), {'income_data_id': income.id})

        # Check if the income record is deleted
        self.assertFalse(Income.objects.filter(id=income.id).exists())

        # Check the response status code and redirection
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('income_data_page'))

