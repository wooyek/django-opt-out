# coding=utf-8
from django import test
from django.shortcuts import resolve_url
from django.test import RequestFactory, TestCase, override_settings
from django.test.utils import TestContextDecorator
from django_powerbank.testing.base import AssertionsMx
from mock import Mock, patch

from django_opt_out import factories, models, signals, views
from django_opt_out.utils import get_opt_out_path


class CaptureSignal(TestContextDecorator):
    """
    A function decorator to connect/disconnect mock handler functions to signals
    """

    def __init__(self, signal, kwarg_name='handler', handler=None):
        super(CaptureSignal, self).__init__(kwarg_name=kwarg_name)
        self.signal = signal
        self.handler = handler or Mock()

    def enable(self):
        self.signal.connect(self.handler)
        return self.handler

    def disable(self):
        self.signal.connect(self.handler)


class OptOutConfirmTests(TestCase):
    @override_settings(OPT_OUT_GOODBYE_VIEW='mocked_goodbye')
    def test_overriden_success_url(self):
        view = views.OptOutConfirm()
        view.object = factories.OptOutFactory(pk=1, secret='7ebc5d464a6485e4b64f', email='ymoore@hotmail.com')
        url = view.get_success_url()
        self.assertEqual('/mocked_goodbye/1/7ebc5d464a6485e4b64f/ymoore@hotmail.com/', url)

    def test_success_url(self):
        view = views.OptOutConfirm()
        view.object = factories.OptOutFactory(pk=1, secret='7ebc5d464a6485e4b64f', email='ymoore@hotmail.com')
        url = view.get_success_url()
        self.assertEqual('/opt-out/success/1/7ebc5d464a6485e4b64f/ymoore@hotmail.com', url)


class OptOutConfirmGetTests(TestCase, AssertionsMx):
    @CaptureSignal(signals.opt_out_visited)
    def test_empty(self, handler):
        url = resolve_url("django_opt_out:OptOutConfirm")
        response = test.Client().get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual({}, response.context_data['form'].errors)
        self.assertTrue(handler.called)

    def test_simple(self):
        url = get_opt_out_path("foo@bar.com")
        response = test.Client().get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual({}, response.context_data['form'].errors)
        self.assertEqual("foo@bar.com", response.context_data['form']['email'].initial)

    def test_with_feedback(self):
        feedback = factories.OptOutFeedbackFactory.create_batch(10)
        url = get_opt_out_path("foo@bar.com")
        response = test.Client().get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual({}, response.context_data['form'].errors)
        choices = [pk for pk, label in response.context_data['form'].fields['feedback'].choices]
        self.assertEqual(set((f.pk for f in feedback)), set(choices))

    def test_only_default_feedback(self):
        feedback = factories.OptOutFeedbackFactory.create_batch(3)
        tag1 = factories.OptOutTagFactory()
        factories.OptOutFeedbackFactory.create_batch(3, tags=(tag1,))
        url = get_opt_out_path("foo@bar.com")
        response = test.Client().get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual({}, response.context_data['form'].errors)
        choices = [pk for pk, label in response.context_data['form'].fields['feedback'].choices]
        self.assertEqual(set((f.pk for f in feedback)), set(choices))

    def test_feedback_based_on_tags(self):
        feedback = factories.OptOutFeedbackFactory.create_batch(3)
        tag1 = factories.OptOutTagFactory()
        feedback.extend(factories.OptOutFeedbackFactory.create_batch(3, tags=(tag1,)))
        tag2 = factories.OptOutTagFactory()
        factories.OptOutFeedbackFactory.create_batch(3, tags=(tag2,))
        tag3 = factories.OptOutTagFactory()
        feedback.extend(factories.OptOutFeedbackFactory.create_batch(3, tags=(tag3,)))
        url = get_opt_out_path("foo@bar.com", tag1.name, tag3.name)
        response = test.Client().get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual({}, response.context_data['form'].errors)
        choices = [pk for pk, label in response.context_data['form'].fields['feedback'].choices]
        self.assertEqual(set((f.pk for f in feedback)), set(choices))

    def test_feedback_checked_by_default(self):
        factories.OptOutFeedbackFactory.create_batch(3)
        feedback = factories.OptOutFeedbackFactory.create_batch(3, default=True)
        url = get_opt_out_path("foo@bar.com")
        response = test.Client().get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual({}, response.context_data['form'].errors)
        initial = response.context_data['form'].fields['feedback'].initial
        self.assertEqual([f.pk for f in feedback], initial)

    def test_default_feedback(self):
        feedback = factories.OptOutFeedbackFactory.create_batch(3, default=True)
        request = RequestFactory().get('/', data={'tag': 'default'})
        view = views.OptOutConfirm(request=request)
        form = view.get_form()
        items = list(form.fields['feedback'].queryset)
        self.assertEqual(set(feedback), set(items))

    def test_default_feedback_on(self):
        feedback = factories.OptOutFeedbackFactory.create_batch(3, default=True)
        request = RequestFactory().get('/', data={'tag': 'default:on'})
        view = views.OptOutConfirm(request=request)
        form = view.get_form()
        items = list(form.fields['feedback'].queryset)
        self.assertEqual(set(feedback), set(items))

    def test_default_feedback_true(self):
        feedback = factories.OptOutFeedbackFactory.create_batch(3, default=True)
        request = RequestFactory().get('/', data={'tag': 'default:true'})
        view = views.OptOutConfirm(request=request)
        form = view.get_form()
        items = list(form.fields['feedback'].queryset)
        self.assertEqual(set(feedback), set(items))

    def test_default_feedback_True(self):
        feedback = factories.OptOutFeedbackFactory.create_batch(3, default=True)
        request = RequestFactory().get('/', data={'tag': 'default:True'})
        view = views.OptOutConfirm(request=request)
        form = view.get_form()
        items = list(form.fields['feedback'].queryset)
        self.assertEqual(set(feedback), set(items))

    def test_default_feedback_1(self):
        feedback = factories.OptOutFeedbackFactory.create_batch(3, default=True)
        request = RequestFactory().get('/', data={'tag': 'default:1'})
        view = views.OptOutConfirm(request=request)
        form = view.get_form()
        items = list(form.fields['feedback'].queryset)
        self.assertEqual(set(feedback), set(items))

    def test_default_feedback_0(self):
        factories.OptOutFeedbackFactory.create_batch(3, default=True)
        request = RequestFactory().get('/', data={'tag': 'default:0'})
        view = views.OptOutConfirm(request=request)
        form = view.get_form()
        self.assertEqual(0, form.fields['feedback'].queryset.count())


@patch('django_opt_out.plugins.sparkpost.hooks.client', Mock())
class OptOutConfirmPostTests(TestCase, AssertionsMx):
    @CaptureSignal(signals.opt_out_submitted)
    def test_just_email(self, handler):
        url = resolve_url("django_opt_out:OptOutConfirm")
        response = test.Client().post(url, data={'email': 'foo@bar.com'})
        self.assertNoFormErrors(response)
        item = models.OptOut.objects.first()
        self.assertIsNotNone(item)
        self.assertEqual(item.email, 'foo@bar.com')
        url = resolve_url("django_opt_out:OptOutSuccess", item.pk, item.secret, item.email)
        self.assertRedirects(response, url)
        self.assertTrue(handler.called)

    def test_comment(self):
        url = resolve_url("django_opt_out:OptOutConfirm")
        response = test.Client().post(url, data={'email': 'foo@bar.com', 'comment': 'Dynda, dynda stryczka cień!'})
        self.assertNoFormErrors(response)
        item = models.OptOut.objects.first()
        self.assertIsNotNone(item)
        self.assertEqual(item.comment, 'Dynda, dynda stryczka cień!')

    def test_valid_tag(self):
        tag = factories.OptOutTagFactory(name='source')
        url = get_opt_out_path("foo@bar.com", "source")
        response = test.Client().post(url, data={'email': 'foo@bar.com'})
        self.assertNoFormErrors(response)
        item = models.OptOut.objects.first()
        item_tag = item.tags.all().first()
        self.assertEqual(tag, item_tag.tag)
        self.assertIsNone(item_tag.value)

    def test_valid_tag_value(self):
        factories.OptOutTagFactory(name='source')
        url = get_opt_out_path("foo@bar.com", "source:some")
        response = test.Client().post(url, data={'email': 'foo@bar.com'})
        self.assertNoFormErrors(response)
        item = models.OptOut.objects.first()
        self.assertEqual('some', item.tags.all().first().value)

    def test_multiple_tags(self):
        factories.OptOutTagFactory(name='source')
        factories.OptOutTagFactory(name='flag')
        url = get_opt_out_path("foo@bar.com", "source:some", "flag")
        response = test.Client().post(url, data={'email': 'foo@bar.com'})
        self.assertNoFormErrors(response)
        item = models.OptOut.objects.first()
        self.assertEqual(['source', 'flag'], list(item.tags.all().values_list('tag__name', flat=True)))

    def test_feedback(self):
        questions = factories.OptOutFeedbackFactory.create_batch(10)[3:7]
        url = get_opt_out_path("foo@bar.com")
        response = test.Client().post(url, data={'email': 'foo@bar.com', 'feedback': [q.pk for q in questions]})
        self.assertNoFormErrors(response)
        item = models.OptOut.objects.first()
        self.assertEqual(set(questions), set(item.feedback.all()))

    def test_confirmed(self):
        url = get_opt_out_path("foo@bar.com")
        response = test.Client().post(url, data={'email': 'foo@bar.com'})
        self.assertNoFormErrors(response)
        item = models.OptOut.objects.first()
        self.assertIsNotNone(item)
        self.assertIsNotNone(item.confirmed)

    @override_settings(OUT_OUT_REQUIRE_CONFIRMATION=False)
    def test_not_confirmed(self):
        url = get_opt_out_path("foo@bar.com")
        response = test.Client().post(url, data={'email': 'foo@bar.com'})
        self.assertNoFormErrors(response)
        item = models.OptOut.objects.first()
        self.assertIsNotNone(item)
        self.assertIsNone(item.confirmed)


class OptOutUpdateGetTests(TestCase, AssertionsMx):
    def test_404(self):
        url = resolve_url("django_opt_out:OptOutUpdate", 2, 'a', 'foo@bar')
        response = test.Client().get(url)
        self.assertEqual(404, response.status_code)

    def test_forbidden_bad_secret(self):
        item = factories.OptOutFactory()
        url = resolve_url("django_opt_out:OptOutUpdate", item.pk, item.secret[:-1], item.email)
        response = test.Client().get(url)
        self.assertEqual(403, response.status_code)

    def test_forbidden_bad_email(self):
        item = factories.OptOutFactory()
        url = resolve_url("django_opt_out:OptOutUpdate", item.pk, item.secret, 'a' + item.email)
        response = test.Client().get(url)
        self.assertEqual(403, response.status_code)

    def test_authorized(self):
        item = factories.OptOutFactory()
        url = resolve_url("django_opt_out:OptOutUpdate", item.pk, item.secret, item.email)
        response = test.Client().get(url)
        self.assertEqual(200, response.status_code)
        self.assertNoFormErrors(response)

    def test_feedback_based_on_saved_tags(self):
        feedback = factories.OptOutFeedbackFactory.create_batch(3)
        tag1 = factories.OptOutTagFactory()
        feedback.extend(factories.OptOutFeedbackFactory.create_batch(3, tags=(tag1,)))
        tag2 = factories.OptOutTagFactory()
        factories.OptOutFeedbackFactory.create_batch(3, tags=(tag2,))
        item = factories.OptOutFactory()
        item.tags.create(tag=tag1)
        url = resolve_url("django_opt_out:OptOutUpdate", item.pk, item.secret, item.email)
        response = test.Client().get(url)
        self.assertEqual(200, response.status_code)
        self.assertNoFormErrors(response)
        choices = [pk for pk, label in response.context_data['form'].fields['feedback'].choices]
        self.assertEqual(set((f.pk for f in feedback)), set(choices))

    def test_initial_feedback(self):
        feedback = factories.OptOutFeedbackFactory.create_batch(7)[3:5]
        item = factories.OptOutFactory()
        item.feedback.add(*feedback)
        url = resolve_url("django_opt_out:OptOutUpdate", item.pk, item.secret, item.email)
        response = test.Client().get(url)
        self.assertEqual(200, response.status_code)
        self.assertNoFormErrors(response)
        choices = set(response.context_data['form'].fields['feedback'].initial)
        self.assertEqual(set((f.pk for f in feedback)), set(choices))


class OptOutUpdatePostTests(TestCase, AssertionsMx):
    def test_save(self):
        item = factories.OptOutFactory()
        url = resolve_url("django_opt_out:OptOutUpdate", item.pk, item.secret, item.email)
        response = test.Client().post(url, data={'email': item.email})
        self.assertNoFormErrors(response)
        self.assertRedirects(response, resolve_url("django_opt_out:OptOutSuccess", item.pk, item.secret, item.email))


@patch('django_opt_out.plugins.sparkpost.hooks.client', Mock())
class OptOutSuccessTests(TestCase, AssertionsMx):
    @CaptureSignal(signals.opt_out_deleted)
    def test_post(self, handler):
        item = factories.OptOutFactory()
        url = resolve_url("django_opt_out:OptOutSuccess", item.pk, item.secret, item.email)
        response = test.Client().post(url)
        self.assertNoFormErrors(response)
        self.assertRedirects(response, resolve_url("django_opt_out:OptOutRemoved"))
        self.assertTrue(handler.called)
