from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client
from expenses_tracker.pdf import convert_html_to_pdf


class ConvertHtmlToPdfTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_convert_html_to_pdf(self):
        # Create HTML content to convert
        source_html = '<html><body><h1>Hello, World!</h1></body></html>'

        # Simulate converting expense report HTML to PDF
        expense_pdf_response = convert_html_to_pdf(source_html, is_expense_report=True)

        # Check if the response status code is 200
        self.assertEqual(expense_pdf_response.status_code, 200)

        # Check if the content type is application/pdf
        self.assertEqual(expense_pdf_response['Content-Type'], 'application/pdf')

