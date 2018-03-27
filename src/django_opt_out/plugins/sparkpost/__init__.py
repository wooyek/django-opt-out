# coding=utf-8
import json
import logging
from smtplib import SMTPAuthenticationError, SMTPServerDisconnected

from django import dispatch
from django.conf import settings
from django.core import mail
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from sparkpost.exceptions import SparkPostAPIException

log = logging.getLogger(__name__)
send_mail_template_signal = dispatch.Signal(providing_args=["message", "template", "ctx"])


def send_email(subject, to, ctx, template_html, template_txt=None, **kwargs):
    """Send rendered message with SparkPost unsubscribe support"""

    html_message, text_message = _render_message(ctx, template_html, template_txt)
    message = _message_factory(html_message, text_message, subject=subject, to=to, **kwargs)
    log.debug("%s: %s", to, subject)

    if 'unsubscribe' in ctx:  # pragma: nocover
        message.extra_headers['List-Unsubscribe'] = "<{}>".format(ctx['unsubscribe'])
        message.extra_headers['X-MSYS-API'] = json.dumps({'options': {'transactional': True}})

    try:
        return _send_robust(message)
    finally:
        send_mail_template_signal.send_robust(sender=send_email, message=message, template_html=template_html, ctx=ctx)


def _message_factory(html_message, text_message, **kwargs):
    to = kwargs.pop('to')
    if not isinstance(to, list):  # pragma: nocover
        to = [to]
    kwargs.setdefault('from_email', settings.DEFAULT_FROM_EMAIL)
    try:
        kwargs.setdefault('reply_to', [settings.DEFAULT_REPLY_TO_EMAIL])
    except AttributeError:
        pass
    message = mail.EmailMultiAlternatives(body=text_message, to=to, **kwargs)
    if html_message:  # pragma: nocover
        message.attach_alternative(html_message, 'text/html')
    return message


def _send_robust(message):
    try:
        return message.send()
    except SparkPostAPIException as ex:  # pragma: nocover
        if ex.status == 1902 or not settings.FAIL_ON_EMAIL_SUPPRESSION:
            logging.error("Email suppression: %s", message.to, exc_info=ex)
        else:
            raise
    except (SMTPServerDisconnected, SMTPAuthenticationError) as ex:  # pragma: nocover
        if not settings.SPARKPOST_RETRY_ONCE:
            raise
        logging.error("", exc_info=ex)
        # Retry once
        return message.send()


def _render_message(ctx, template_html, template_txt):
    html_message = render_to_string(template_html, ctx)
    text_message = None
    if template_txt is None:  # pragma: nocover
        template_txt = (template_html.replace(".html", ".jinja2"), template_html.replace(".html", ".txt"))
    try:
        text_message = render_to_string(template_txt, ctx)
    except TemplateDoesNotExist:
        if settings.SPARKPOST_HTML2TXT:
            import html2text
            text_message = html2text.html2text(html_message)
    return html_message, text_message
