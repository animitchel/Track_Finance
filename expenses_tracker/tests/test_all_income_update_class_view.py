from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from expenses_tracker.models import Income


class TestAllIncomeUpdateAndDeletePage(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_get_context_data(self):
        # Log in the test user
        self.client.login(username='testuser', password='password')

        # Create a test income object
        income = Income.objects.create(
            user=self.user,
            amount=100.0,
            category='Test Source'
        )

        # Make a GET request to the view
        response = self.client.get(reverse('income_update', kwargs={'pk': income.pk}))

        # Check that the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Check the context data returned by the view
        self.assertTrue('update' in response.context)
        self.assertTrue('user_status' in response.context)
        self.assertTrue('current_year' in response.context)
        self.assertTrue('object' in response.context)
        self.assertTrue('header_name' in response.context)
        self.assertEqual(response.context['update'], True)
        self.assertEqual(response.context['user_status'], True)  # Assuming user is authenticated
        self.assertEqual(response.context['object'], income.id)
        self.assertEqual(response.context['header_name'], 'Update Income')
