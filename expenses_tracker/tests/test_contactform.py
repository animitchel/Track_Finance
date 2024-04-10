from django.test import TestCase
from expenses_tracker.form_models import ContactForm
from django.forms import ValidationError


class ContactFormTest(TestCase):
    def test_valid_form(self):
        form_data = {
            'name': 'John Doe',
            'email': 'johndoe@example.com',
            'phone': '+12125552368',
            'message': 'This is a test message.'
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {
            'name': '',  # Missing required field
            'email': 'invalid_email',  # Invalid email format
            'phone': '+123',  # Phone number too short
            'message': 'Short'  # Message too short
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 4)  # Expecting errors for each field

    def test_clean_your_field(self):
        form_data = {
            'name': 'John Doe',
            'email': 'johndoe@example.com',
            'phone': '+12125552368',
            'message': 'This is a test message.'
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Test non-ASCII characters in message and name
        form.cleaned_data['message'] = 'This is a test message with non-ASCII character 😊.'
        form.cleaned_data['name'] = 'John Doe é'
        with self.assertRaises(ValidationError):
            form.clean_your_field()
