from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.core.mail import send_mail, EmailMessage
from django.conf import settings

from xhtml2pdf import pisa

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
    if not pdf.err:
        return result.getvalue()
    return None



def send_email(order, name, email):
	pdf = render_to_pdf('shopping_cart/invoice.html', order)

	msg = EmailMessage(
		'Invoice', 
		"""Dear {}
 
Attachment is your invoice, our goal is to serve clients to the best of our ability, we appreciate the opportunity to serve you and look forward to do business with you again.\n
In the meantime, if you have any questions or require assistance, please feel free to contact us at below addresses. """.format(name),

		settings.EMAIL_HOST_USER, 
		[str(email)]
		)

	msg.attach('invoice.pdf', pdf, 'application/pdf')
	return msg.send()
