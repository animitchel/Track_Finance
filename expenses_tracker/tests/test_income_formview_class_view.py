from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import datetime
from expenses_tracker.models import Income
from expenses_tracker.form_models import IncomeForm
from expenses_tracker.views import IncomeFormView


class IncomeFormViewTestCase(TestCase):
    def setUp(self):
        # Create a test client
        self.client = Client()

        # Create a user for testing
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_get_request(self):
        # Log in the user
        self.client.force_login(self.user)

        # Make a GET request to the view
        response = self.client.get(reverse('add_income_page'))

        # Check the response status code
        self.assertEqual(response.status_code, 200)

        # Check if the form is rendered correctly
        self.assertIsInstance(response.context['form'], IncomeForm)

    def test_post_request_valid_form(self):
        # Log in the user
        self.client.force_login(self.user)

        # Define form data
        form_data = {
            'amount': 100,
            'category': 'business income',
            'notes': 'Test notes for testing',
            'recurring_transaction': False
            # Add other form fields as needed
        }

        form = IncomeForm(data=form_data)

        # Check that the form is valid
        self.assertTrue(form.is_valid())

        # Make a POST request to the view with form data
        request = self.client.post(reverse('add_income_page'), form_data)

        # Create an instance of the view and call form_valid method
        view = IncomeFormView()
        view.request = request
        view.request.user = self.user
        response = view.form_valid(form)

        # Check if the form submission redirects to the success URL
        self.assertEqual(response.status_code, 302)

        # Check if the income record is created
        self.assertTrue(Income.objects.filter(user=self.user, amount=100).exists())
