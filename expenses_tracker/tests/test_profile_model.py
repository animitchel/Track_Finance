from django.test import TestCase
from django.contrib.auth.models import User
from expenses_tracker.models import Profile


class ProfileModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user for testing
        cls.user = User.objects.create(username='testuser')

    def test_profile_fields(self):
        # Create a profile instance
        profile = Profile.objects.create(
            currency='$',
            first_name='John',
            last_name='Doe',
            occupation='Developer',
            city='New York',
            country='USA',
            phone_number='+1234567890',
            user=self.user
        )

        # Test fields
        self.assertEqual(profile.currency, '$')
        self.assertEqual(profile.first_name, 'John')
        self.assertEqual(profile.last_name, 'Doe')
        self.assertEqual(profile.occupation, 'Developer')
        self.assertEqual(profile.city, 'New York')
        self.assertEqual(profile.country, 'USA')
        self.assertEqual(profile.phone_number, '+1234567890')
        self.assertEqual(profile.user, self.user)

    def test_currency_choices(self):
        # Get currency choices from the Profile model
        currency_choices = dict(Profile.CURRENCY_CHOICES)

        # Test if each currency choice is in the currency choices
        for choice_key, choice_value in currency_choices.items():
            self.assertIn(choice_key, dict(Profile.CURRENCY_CHOICES).keys())
