from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_form(*, form, template, subject):
    """Send given form to email."""

    message = render_to_string(
        template,
        {
            'form': form.cleaned_data,
            'base_url': settings.BASE_URL,
            'site_info': settings.SITE_INFO
        },
    )

    send_mail(
        subject='Stroyprombeton | {}'.format(subject),
        message=message,
        from_email=settings.EMAIL_SENDER,
        recipient_list=[settings.SHOP_EMAIL],
        html_message=message
    )
