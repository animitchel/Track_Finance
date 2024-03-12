from io import BytesIO
from django.http import HttpResponse
from xhtml2pdf import pisa


# def render_template(template_html, context_data=None):
#     template = Template(template_html)
#     context_ = Context(context_data)
#     return template.render(context_)


# Utility function to convert HTML to PDF
# from django.template import Context, Template
# def convert_html_to_pdf(source_html):
#     result = HttpResponse(content_type='application/pdf')
#     result['Content-Disposition'] = 'attachment; filename="Expenses_Report.pdf"'
#
#     # Convert rendered HTML to PDF
#     pisa_status = pisa.CreatePDF(
#         source_html.encode(encoding='utf-8'),  # the rendered HTML to convert
#         dest=result)  # response object to receive result
#
#     if pisa_status.err:
#         return HttpResponse('PDF conversion failed', status=500)
#
#     return result


def convert_html_to_pdf(source_html):
    # Initialize HttpResponse object to store the PDF result
    result = HttpResponse(content_type='application/pdf')
    result['Content-Disposition'] = 'attachment; filename="Expenses_Report.pdf"'

    # Create a BytesIO object to capture the PDF content
    pdf_content = BytesIO()

    # Ensure UTF-8 encoding for source HTML content
    encoded_html = source_html.encode(encoding='utf-8')

    # Convert rendered HTML to PDF
    pisa_status = pisa.CreatePDF(
        encoded_html,  # the rendered HTML to convert
        dest=pdf_content)  # BytesIO object to receive result

    # Check the conversion status
    if pisa_status.err:
        # Return an error response if PDF conversion failed
        return HttpResponse('PDF conversion failed', status=500)

    # Reset the file pointer of the BytesIO object to the beginning
    pdf_content.seek(0)

    # Write the PDF content to the result HttpResponse object
    result.write(pdf_content.read())

    # Return the result HttpResponse object containing the PDF content
    return result
