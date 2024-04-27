from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from expenses_tracker.models import Income


class TestDeleteIncomeView(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_delete_income(self):
        # Log in the test user
        self.client.login(username='testuser', password='password')

        # Create an income for testing
        income = Income.objects.create(
            user=self.user,
            amount=100.0,
            category='Test Source'
        )

        # Make a POST request to delete the income
        response = self.client.post(reverse('income_delete', kwargs={'pk': income.pk}))

        # Check that the income is deleted
        self.assertFalse(Income.objects.filter(id=income.id).exists())

        # Check that the view redirects to the correct URL after deletion
        self.assertRedirects(response, reverse('income_data_page'))
