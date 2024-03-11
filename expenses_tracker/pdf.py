from io import BytesIO
from django.template.loader import render_to_string, get_template
from django.http import HttpResponse
from django.template import Context, Template
from xhtml2pdf import pisa


# def render_pdf(template_name, context, request=None):
#     template = get_template(template_name)
#     html = template.render(context)
#     result = BytesIO()
#     pdf = pisa.pisaDocument(BytesIO(html.encode('utf-8')), result)
#     if not pdf.err:
#         response = HttpResponse(result.getvalue(), content_type='application/pdf')
#         return response
#     return None
# # 'cp1252'


def render_template(template_html, context_data=None):
    template = Template(template_html)
    context_ = Context(context_data)
    return template.render(context_)


# Utility function to convert HTML to PDF
def convert_html_to_pdf(source_html):
    result = HttpResponse(content_type='application/pdf')
    result['Content-Disposition'] = 'attachment; filename="Expenses_Report.pdf"'

    # Render template with context data
    rendered_html = render_template(source_html)

    # Convert rendered HTML to PDF
    pisa_status = pisa.CreatePDF(
        rendered_html.encode(encoding='utf-8'),  # the rendered HTML to convert
        dest=result)  # response object to receive result

    if pisa_status.err:
        return HttpResponse('PDF conversion failed', status=500)
    return result

