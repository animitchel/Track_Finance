from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from expenses_tracker.models import Budget
from expenses_tracker.form_models import BudgetForm
from expenses_tracker.views import AddBudgetView
from django.core.cache import cache


class AddBudgetViewTestCase(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_form_valid(self):
        # Create a sample form instance
        form_data = {'amount': 100,
                     'category': 'Housing',
                     'duration': '1 week'
                     }

        form = BudgetForm(data=form_data)

        # Check that the form is valid
        self.assertTrue(form.is_valid())

        # Create a sample request object
        request = self.client.post(reverse('add_budget_page'), data=form_data)

        # Create an instance of the view and call form_valid method
        view = AddBudgetView()
        view.request = request
        view.request.user = self.user
        response = view.form_valid(form)

        # Check that the response is a redirect
        self.assertEqual(response.status_code, 302)

        # Check that the budget object was created with the correct values
        budget = Budget.objects.get(id=1)
        self.assertEqual(budget.budget, 100)

    def test_get_context_data(self):
        # Make GET request to the view
        response = self.client.get(reverse('add_budget_page'))

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
