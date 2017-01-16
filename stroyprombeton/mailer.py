from django.conf import settings
from django.core.mail import send_mail, get_connection, EmailMultiAlternatives
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
        from_email=settings.SHOP_EMAIL,
        recipient_list=[settings.SHOP_EMAIL],
        html_message=message
    )


def send_form_with_files(*, form, files, template, subject, **context):
    message = render_to_string(
        template,
        {
            'form': form.cleaned_data,
            'site_info': settings.SITE_INFO,
            **context
        },
    )

    mail = EmailMultiAlternatives(
        subject='Stroyprombeton | {}'.format(subject),
        body=message,
        from_email=settings.SHOP_EMAIL,
        to=[settings.SHOP_EMAIL],
        connection=get_connection()
    )

    mail.attach_alternative(message, 'text/html')  # Attach message

    for file in files:  # Attach files
        mail.attach(filename=file._name, content=file.read(), mimetype=file.content_type)

    mail.send()
