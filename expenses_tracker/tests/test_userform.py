from django.test import TestCase
from django.contrib.auth.models import User
from expenses_tracker.form_models import UserForm


class TestUserForm(TestCase):
    def test_user_form_valid(self):
        # Define test data
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword'
        }

        # Create form instance with test data
        form = UserForm(data=form_data)

        # Test form validation
        self.assertTrue(form.is_valid())

        # Test form save
        user = form.save()

        # Test user creation
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, form_data['username'])
        self.assertEqual(user.email, form_data['email'])

    def test_user_form_invalid(self):
        # Define invalid test data (missing required fields)
        form_data = {}

        # Create form instance with invalid test data
        form = UserForm(data=form_data)

        # Test form validation
        self.assertFalse(form.is_valid())

        # Test error messages
        self.assertIn('username', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('password', form.errors)

    def test_password_min_length(self):
        """test password lesser than minimum length 10 characters will raise an error"""
        form_data = {
            'username': 'test_username',
            'password': '12345',
            'email': 'test@example.com',
        }

        # Create form instance with invalid test data
        form = UserForm(data=form_data)

        # Test form validation
        self.assertFalse(form.is_valid())

        # Test error messages
        self.assertIn('password', form.errors)

    def test_incorrect_email(self):
        """test incorrect email raises an error"""
        form_data = {
            'username': 'test_username',
            'password': '1234567890',
            'email': 'testexample.com',
        }
        form = UserForm(data=form_data)

        self.assertFalse(form.is_valid())

        self.assertIn('email', form.errors)



























