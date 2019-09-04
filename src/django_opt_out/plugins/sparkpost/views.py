# coding=utf-8
import json
import logging

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from ...signals import send_signal
from . import signals

log = logging.getLogger(__name__)


class SparkPostUnsubscribeWebhook(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(SparkPostUnsubscribeWebhook, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode("UTF-8"))
        self.process_data(data)
        return HttpResponse("Thx!")

    def process_data(self, data):
        log.debug("data: %s", data)
        for entry in data:
            event = entry.get('msys', {}).get('unsubscribe_event', {})
            event_type = event.get('type')
            if event_type == 'list_unsubscribe':
                email = event['raw_rcpt_to']
                send_signal(signals.list_unsubscribe, self.__class__, request=self.request, email=email, data=entry)
            elif event_type == 'link_unsubscribe':
                email = event['raw_rcpt_to']
                send_signal(signals.link_unsubscribe, self.__class__, request=self.request, email=email, data=entry)
