from six import string_types
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from premailer import transform


def send_game_accepted(user, game):
    context = {
        'username': user.username,
        'name': game.name,
        'game_url': game.get_absolute_url()
    }
    subject = u"Your game submission for '{}' has been accepted!".format(game.name)
    return send_email('game_accepted', context, subject, user.email)


def send_account_creation(user, confirmation_link):
    context = {
        'username': user.username,
        'confirmation_link': confirmation_link
    }
    subject = 'Welcome to Lutris.net'
    return send_email('account_creation', context, subject, user.email)


def send_email(template, context, subject, recipients, sender=None):
    if not settings.SEND_EMAILS:
        return
    context.update({
        'STATIC_URL': settings.STATIC_URL,
        'MEDIA_URL': settings.MEDIA_URL,
    })
    sender = sender or settings.DEFAULT_FROM_EMAIL
    if isinstance(recipients, string_types):
        recipients = [recipients]
    subject = u"{} {}".format(settings.EMAIL_SUBJECT_PREFIX, subject)
    text_part = render_to_string('emails/{}.txt'.format(template), context)
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_part,
        to=recipients,
        from_email=sender
    )
    html_body = render_to_string('emails/{}.html'.format(template), context)
    html_part = transform(html_body, base_url='http://lutris.net')
    msg.attach_alternative(html_part, "text/html")
    return msg.send(False)
