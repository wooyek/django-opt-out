# coding=utf-8
import logging

import sparkpost
from django.conf import settings
from django.dispatch import receiver
from django.utils.functional import SimpleLazyObject
from sparkpost.exceptions import SparkPostAPIException

from . import signals
from ... import signals as opt_out

log = logging.getLogger(__name__)


@receiver(signals.list_unsubscribe, dispatch_uid="create_opt_out")
@receiver(signals.link_unsubscribe, dispatch_uid="create_opt_out")
def create_opt_out(sender, request, email, data, **kwargs):
    log.debug("OptOut %s on SparkPost unsubscribe event", email)
    from django_opt_out.models import OptOut
    OptOut.objects.create(email=email, data=data)


@receiver(opt_out.opt_out_submitted, dispatch_uid="suppress_email")
def suppress_email(sender, view, request, opt_out, **kwargs):
    log.debug("Creating suppression for %s in SparkPost", opt_out.email)
    client.suppression_list.create({
        'email': opt_out.email,
        'transactional': True,
        'non-transactional': True,
        'description': 'Created through: {}'.format(opt_out)}
    )


@receiver(opt_out.opt_out_deleted, dispatch_uid="remove_suppression")
def remove_suppression(sender, view, request, opt_out, **kwargs):
    log.debug("Removing suppression %s from SparkPost", opt_out.email)
    try:
        client.suppression_list.delete(opt_out.email)
    except SparkPostAPIException as ex:
        if ex.status != 404:
            raise ex


def get_client(setting='SPARKPOST_API_KEY'):
    return sparkpost.SparkPost(getattr(settings, setting, None))


client = SimpleLazyObject(get_client)
