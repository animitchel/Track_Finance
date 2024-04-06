from django.test import TestCase
from django.contrib.auth import get_user_model
from expenses_tracker.models import Profile
from django.db.utils import IntegrityError


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserModelTests(TestCase):
    """Test unauthenticated user"""

    def test_user_create(self):
        payload = {
            'username': 'test_username',
            'password': 'test_password123456',
        }

        user = create_user(**payload)

        self.assertEqual(user.username, payload['username'])
        self.assertTrue(user.check_password(payload['password']))

    def test_user_already_exists(self):
        """test creating a user with that username already exists"""
        payload = {
            'username': 'test_username',
            'password': 'test_password123456',
        }
        create_user(**payload)
        with self.assertRaises(IntegrityError):
            create_user(**payload)

        self.assertRaises(IntegrityError)

    def test_permission_does_not_exist(self):
        """
        test creating a user to see if some permissions are not allowed,
        and testing relations between User and Profile
        """
        payload = {
            'username': 'test_username',
            'password': 'test_password123456',
        }
        user = create_user(**payload)
        profile = Profile.objects.create(user_id=user.id)

        self.assertEqual(user.is_staff, False)
        self.assertEqual(user.is_superuser, False)
        self.assertEqual(user.is_active, True)
        self.assertEqual(profile.user_id, user.id)


class TestGetUserModel(TestCase):
    def test_get_user_model(self):
        # Retrieve the user model using get_user_model()
        User = get_user_model()

        # Ensure the user model exists
        self.assertIsNotNone(User)

        # Ensure the user model is the expected model
        self.assertEqual(User, get_user_model())

        # Create a test user
        username = 'testuser'
        email = 'testuser@example.com'
        password = 'testpassword'
        user = User.objects.create_user(username=username, email=email, password=password)

        # Ensure the created user exists
        self.assertIsNotNone(user)
        self.assertEqual(user.username, username)
        self.assertEqual(user.email, email)

        # Ensure the created user can authenticate with the provided password
        self.assertTrue(User.objects.filter(username=username).exists())
        self.assertTrue(User.objects.filter(email=email).exists())
        self.assertTrue(user.check_password(password))






