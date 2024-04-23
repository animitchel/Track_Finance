from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from expenses_tracker.models import Budget
from expenses_tracker.views import BudgetOverviewView


class BudgetOverviewViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_get_queryset(self):
        # Create sample data for testing
        budget1 = Budget.objects.create(user_id=self.user.id, budget=100000, duration='1 week', category='Education',
                                        amount=100000)
        budget2 = Budget.objects.create(user_id=self.user.id, budget=1000, duration='2 weeks', category='Education',
                                        amount=1000)

        # Set session data for filtering
        self.client.session['filter_category'] = 'Utilities'
        self.client.session['sort_order'] = 'Ascending'

        # Make GET request to the view
        response = self.client.get(reverse('budget-overview_page'))

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        # Create sample data for testing
        budget = Budget.objects.create(user_id=self.user.id, duration='1 week', category='Education',
                                       amount=10000)

        # Make POST request to the view
        response = self.client.post(reverse('budget-overview_page'), {'budget_overview_id': budget.id})

        # Check that the response status code is 302 (redirect)
        self.assertEqual(response.status_code, 302)

        # Check that the budget object was deleted as expected
        with self.assertRaises(Budget.DoesNotExist):
            Budget.objects.get(id=budget.id)

    def test_get_context_data(self):
        # Make GET request to the view
        response = self.client.get(reverse('budget-overview_page'))

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
