from django.test import TestCase
from expenses_tracker.form_models import ProfileForm


class TestProfileForm(TestCase):

    def test_form_valid(self):
        # Define test data
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'occupation': 'Software Engineer',
            'city': 'New York',
            'country': 'USA',
            'phone_number': '+1234567890',
            'currency': '$',
        }

        # Create form instance with test data
        form = ProfileForm(data=form_data)

        # Test form validation
        self.assertTrue(form.is_valid())

    def test_form_invalid(self):
        # Define invalid test data (missing required fields)
        form_data = {}

        # Create form instance with invalid test data
        form = ProfileForm(data=form_data)

        # Test form validation
        self.assertFalse(form.is_valid())

        # Test error messages
        self.assertIn('currency', form.errors)
