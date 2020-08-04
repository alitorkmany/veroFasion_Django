import os
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from email.mime.image import MIMEImage
from django.conf import settings

def send_email(to_mail, mail_template, context):
	html_content = render_to_string(mail_template, context)
	text_content = render_to_string('vero_fasion/mail.txt', context)
	subject = 'Explore the world of Vero Fahsion'
	sender = settings.DEFAULT_FROM_EMAIL
	msg = EmailMultiAlternatives(subject, text_content, sender, [to_mail])

	msg.attach_alternative(html_content, "text/html")

	msg.mixed_subtype = 'related'

	for f in ['logo.png', 'women.png', 'men.png', 'kid.png', 'sale.png']:
		fp = open(os.path.join(os.path.dirname(__file__), 'mail_static', f), 'rb')
		msg_img = MIMEImage(fp.read())
		fp.close()
		msg_img.add_header('Content-ID', '<{}>'.format(f))
		msg.attach(msg_img)

	msg.send()
