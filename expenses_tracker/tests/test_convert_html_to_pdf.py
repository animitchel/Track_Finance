from django.test import TestCase
from django.http import HttpResponse
from unittest.mock import patch, Mock
from io import BytesIO
from expenses_tracker.pdf import convert_html_to_pdf


class ConvertHtmlToPdfTests(TestCase):
    @patch('expenses_tracker.pdf.BytesIO')
    @patch('expenses_tracker.pdf.pisa')
    def test_convert_html_to_pdf_expense_report(self, mock_pisa, mock_bytesio):
        mock_bytesio_instance = Mock(spec=BytesIO)
        mock_bytesio.return_value = mock_bytesio_instance
        mock_pisa.CreatePDF.return_value = Mock(err=False)

        source_html = "<html><body><h1>Hello World!</h1></body></html>"

        response = convert_html_to_pdf(source_html, is_expense_report=True)

        mock_pisa.CreatePDF.assert_called_once_with(
            source_html.encode(encoding='utf-8'),
            dest=mock_bytesio_instance
        )

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="Expenses_Report.pdf"')

    @patch('expenses_tracker.pdf.BytesIO')
    @patch('expenses_tracker.pdf.pisa')
    def test_convert_html_to_pdf_income_report(self, mock_pisa, mock_bytesio):
        mock_bytesio_instance = Mock(spec=BytesIO)
        mock_bytesio.return_value = mock_bytesio_instance
        mock_pisa.CreatePDF.return_value = Mock(err=False)

        source_html = "<html><body><h1>Hello World!</h1></body></html>"

        response = convert_html_to_pdf(source_html, is_expense_report=False)

        mock_pisa.CreatePDF.assert_called_once_with(
            source_html.encode(encoding='utf-8'),
            dest=mock_bytesio_instance
        )

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="Incomes_Report.pdf"')

    @patch('expenses_tracker.pdf.BytesIO')
    @patch('expenses_tracker.pdf.pisa')
    def test_convert_html_to_pdf_conversion_failure(self, mock_pisa, mock_bytesio):
        mock_bytesio_instance = Mock(spec=BytesIO)
        mock_bytesio.return_value = mock_bytesio_instance
        mock_pisa.CreatePDF.return_value = Mock(err=True)

        source_html = "<html><body><h1>Hello World!</h1></body></html>"

        response = convert_html_to_pdf(source_html, is_expense_report=False)

        mock_pisa.CreatePDF.assert_called_once_with(
            source_html.encode(encoding='utf-8'),
            dest=mock_bytesio_instance
        )

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.content.decode(), 'PDF conversion failed')
        self.assertEqual(response.status_code, 500)
