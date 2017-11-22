# coding=utf-8
from django import test
from django.shortcuts import resolve_url
from django.test import TestCase
from django.test.utils import override_settings
from mock import patch

from django_opt_out.models import OptOut
from django_opt_out.plugins.sparkpost import signals
from tests.test_views import CaptureSignal


class SparkPostHookTests(TestCase):
    def test_opt_out_created(self):
        self.assertEqual(0, OptOut.objects.all().count())
        url = resolve_url('django_opt_out_sparkpost:SparkPostUnsubscribeWebhook')
        test.Client().post(url, data=list_unsubscribe, content_type="application/json")
        opt_out = OptOut.objects.all().first()
        self.assertEqual('recipient@example.com', opt_out.email)
        self.assertIsNotNone(opt_out.data)

    @CaptureSignal(signals.list_unsubscribe)
    def test_list_unsubscribe(self, handler):
        url = resolve_url('django_opt_out_sparkpost:SparkPostUnsubscribeWebhook')
        test.Client().post(url, data=list_unsubscribe, content_type="application/json")
        self.assertTrue(handler.called)
        args, kwargs = handler.call_args
        self.assertEqual('recipient@example.com', kwargs['email'])

    @CaptureSignal(signals.link_unsubscribe)
    def test_link_unsubscribe(self, handler):
        url = resolve_url('django_opt_out_sparkpost:SparkPostUnsubscribeWebhook')
        test.Client().post(url, data=link_unsubscribe, content_type="application/json")
        self.assertTrue(handler.called)
        args, kwargs = handler.call_args
        self.assertEqual('recipient@example.com', kwargs['email'])

    @CaptureSignal(signals.list_unsubscribe, 'list_handler')
    @CaptureSignal(signals.link_unsubscribe, 'link_handler')
    def test_multi(self, link_handler, list_handler):
        url = resolve_url('django_opt_out_sparkpost:SparkPostUnsubscribeWebhook')
        test.Client().post(url, data=unsubscribe_multiple, content_type="application/json")

        self.assertTrue(link_handler.called)
        args, kwargs = link_handler.call_args
        self.assertEqual('recipient@example.com', kwargs['email'])

        self.assertTrue(list_handler.called)
        args, kwargs = list_handler.call_args
        self.assertEqual('recipient@example.com', kwargs['email'])

    @override_settings(SPARKPOST_API_KEY='not-valid')
    @patch('django_opt_out.plugins.sparkpost.client.suppression_list.create')
    def test_confirm_creates_suppression(self, create):
        url = resolve_url("django_opt_out:OptOutConfirm")
        test.Client().post(url, data={'email': 'foo@bar.com'})
        self.assertTrue(create.called)

list_unsubscribe = """[{"msys":{"unsubscribe_event":{"type":"list_unsubscribe","campaign_id":"Example Campaign Name","customer_id":"1","delv_method":"esmtp","event_id":"92356927693813856","friendly_from":"sender@example.com","ip_address":"127.0.0.1","ip_pool":"Example-Ip-Pool","mailfrom":"recipient@example.com","message_id":"000443ee14578172be22","msg_from":"sender@example.com","msg_size":"1337","num_retries":"2","queue_time":"12","rcpt_meta":{"customKey":"customValue"},"rcpt_tags":["male","US"],"rcpt_to":"recipient@example.com","raw_rcpt_to":"recipient@example.com","rcpt_type":"cc","routing_domain":"example.com","sending_ip":"127.0.0.1","subaccount_id":"101","subject":"Summer deals are here!","template_id":"templ-1234","template_version":"1","timestamp":"1454442600","transmission_id":"65832150921904138"}}}]"""  # noqa E501
link_unsubscribe = """[{"msys":{"unsubscribe_event":{"type":"link_unsubscribe","campaign_id":"Example Campaign Name","customer_id":"1","delv_method":"esmtp","event_id":"92356927693813856","friendly_from":"sender@example.com","ip_address":"127.0.0.1","ip_pool":"Example-Ip-Pool","mailfrom":"recipient@example.com","message_id":"000443ee14578172be22","msg_from":"sender@example.com","msg_size":"1337","num_retries":"2","queue_time":"12","rcpt_meta":{"customKey":"customValue"},"rcpt_tags":["male","US"],"rcpt_to":"recipient@example.com","raw_rcpt_to":"recipient@example.com","rcpt_type":"cc","routing_domain":"example.com","sending_ip":"127.0.0.1","subaccount_id":"101","subject":"Summer deals are here!","template_id":"templ-1234","template_version":"1","timestamp":"1454442600","transmission_id":"65832150921904138","user_agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36"}}}]"""  # noqa E501
unsubscribe_multiple = """
[
  {
    "msys": {
      "unsubscribe_event": {
        "type": "list_unsubscribe",
        "campaign_id": "Example Campaign Name",
        "customer_id": "1",
        "delv_method": "esmtp",
        "event_id": "92356927693813856",
        "friendly_from": "sender@example.com",
        "ip_address": "127.0.0.1",
        "ip_pool": "Example-Ip-Pool",
        "mailfrom": "recipient@example.com",
        "message_id": "000443ee14578172be22",
        "msg_from": "sender@example.com",
        "msg_size": "1337",
        "num_retries": "2",
        "queue_time": "12",
        "rcpt_meta": {
          "customKey": "customValue"
        },
        "rcpt_tags": [
          "male",
          "US"
        ],
        "rcpt_to": "recipient@example.com",
        "raw_rcpt_to": "recipient@example.com",
        "rcpt_type": "cc",
        "routing_domain": "example.com",
        "sending_ip": "127.0.0.1",
        "subaccount_id": "101",
        "subject": "Summer deals are here!",
        "template_id": "templ-1234",
        "template_version": "1",
        "timestamp": "1454442600",
        "transmission_id": "65832150921904138"
      }
    }
  },
  {
    "msys": {
      "unsubscribe_event": {
        "type": "link_unsubscribe",
        "campaign_id": "Example Campaign Name",
        "customer_id": "1",
        "delv_method": "esmtp",
        "event_id": "92356927693813856",
        "friendly_from": "sender@example.com",
        "ip_address": "127.0.0.1",
        "ip_pool": "Example-Ip-Pool",
        "mailfrom": "recipient@example.com",
        "message_id": "000443ee14578172be22",
        "msg_from": "sender@example.com",
        "msg_size": "1337",
        "num_retries": "2",
        "queue_time": "12",
        "rcpt_meta": {
          "customKey": "customValue"
        },
        "rcpt_tags": [
          "male",
          "US"
        ],
        "rcpt_to": "recipient@example.com",
        "raw_rcpt_to": "recipient@example.com",
        "rcpt_type": "cc",
        "routing_domain": "example.com",
        "sending_ip": "127.0.0.1",
        "subaccount_id": "101",
        "subject": "Summer deals are here!",
        "template_id": "templ-1234",
        "template_version": "1",
        "timestamp": "1454442600",
        "transmission_id": "65832150921904138",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36"
      }
    }
  }
]
"""
