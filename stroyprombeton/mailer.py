from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def send_form(*, form, template, subject):
    """Send given form in a email."""

    email_template = render_to_string(template,
                                      {'form': form.cleaned_data})

    send_mail(subject='Stroyprombeton | {}'.format(subject),
              message=email_template,
              from_email=settings.SHOP_EMAIL,
              recipient_list=[settings.SHOP_EMAIL],
              html_message=email_template)
