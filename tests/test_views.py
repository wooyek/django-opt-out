# coding=utf-8
import logging
from django import test
from django.shortcuts import resolve_url
from django.test import TestCase, override_settings
from django_powerbank.testing.base import AssertionsMx


from django_opt_out import models, factories
from django_opt_out.utils import get_opt_out_url


class OptOutConfirmGetTests(TestCase, AssertionsMx):
    def test_empty(self):
        url = resolve_url("django_opt_out:OptOutConfirm")
        response = test.Client().get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual({}, response.context_data['form'].errors)

    def test_simple(self):
        url = get_opt_out_url("foo@bar.com")
        response = test.Client().get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual({}, response.context_data['form'].errors)
        self.assertEqual("foo@bar.com", response.context_data['form']['email'].initial)

    def test_with_feedback(self):
        feedback = factories.OptOutFeedbackFactory.create_batch(10)
        url = get_opt_out_url("foo@bar.com")
        response = test.Client().get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual({}, response.context_data['form'].errors)
        choices = [pk for pk, label in response.context_data['form'].fields['feedback'].choices]
        self.assertEqual(set((f.pk for f in feedback)), set(choices))

    def test_only_default_feedback(self):
        feedback = factories.OptOutFeedbackFactory.create_batch(3)
        tag1 = factories.OptOutTagFactory()
        factories.OptOutFeedbackFactory.create_batch(3, tags=(tag1,))
        url = get_opt_out_url("foo@bar.com")
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
        url = get_opt_out_url("foo@bar.com", tag1.name, tag3.name)
        response = test.Client().get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual({}, response.context_data['form'].errors)
        choices = [pk for pk, label in response.context_data['form'].fields['feedback'].choices]
        self.assertEqual(set((f.pk for f in feedback)), set(choices))

    def test_feedback_checked_by_default(self):
        factories.OptOutFeedbackFactory.create_batch(3)
        feedback = factories.OptOutFeedbackFactory.create_batch(3, default=True)
        url = get_opt_out_url("foo@bar.com")
        response = test.Client().get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual({}, response.context_data['form'].errors)
        initial = response.context_data['form'].fields['feedback'].initial
        self.assertEqual([f.pk for f in feedback], initial)


class OptOutConfirmPostTests(TestCase, AssertionsMx):
    def test_just_email(self):
        url = resolve_url("django_opt_out:OptOutConfirm")
        response = test.Client().post(url, data={'email': 'foo@bar.com'})
        self.assertNoFormErrors(response)
        item = models.OptOut.objects.first()
        self.assertIsNotNone(item)
        self.assertEqual(item.email, 'foo@bar.com')
        url = resolve_url("django_opt_out:OptOutSuccess", item.pk, item.secret, item.email)
        self.assertRedirects(response, url)

    def test_comment(self):
        url = resolve_url("django_opt_out:OptOutConfirm")
        response = test.Client().post(url, data={'email': 'foo@bar.com', 'comment': 'Dynda, dynda stryczka cień!'})
        self.assertNoFormErrors(response)
        item = models.OptOut.objects.first()
        self.assertIsNotNone(item)
        self.assertEqual(item.comment, 'Dynda, dynda stryczka cień!')

    def test_valid_tag(self):
        tag = factories.OptOutTagFactory(name='source')
        url = get_opt_out_url("foo@bar.com", "source")
        response = test.Client().post(url, data={'email': 'foo@bar.com'})
        self.assertNoFormErrors(response)
        item = models.OptOut.objects.first()
        item_tag = item.tags.all().first()
        self.assertEqual(tag, item_tag.tag)
        self.assertIsNone(item_tag.value)

    def test_valid_tag_value(self):
        tag = factories.OptOutTagFactory(name='source')
        url = get_opt_out_url("foo@bar.com", "source:some")
        response = test.Client().post(url, data={'email': 'foo@bar.com'})
        self.assertNoFormErrors(response)
        item = models.OptOut.objects.first()
        self.assertEqual('some', item.tags.all().first().value)

    def test_multiple_tags(self):
        factories.OptOutTagFactory(name='source')
        factories.OptOutTagFactory(name='flag')
        url = get_opt_out_url("foo@bar.com", "source:some", "flag")
        response = test.Client().post(url, data={'email': 'foo@bar.com'})
        self.assertNoFormErrors(response)
        item = models.OptOut.objects.first()
        self.assertEqual(['source', 'flag'], list(item.tags.all().values_list('tag__name', flat=True)))

    def test_feedback(self):
        questions = factories.OptOutFeedbackFactory.create_batch(10)[3:7]
        url = get_opt_out_url("foo@bar.com")
        response = test.Client().post(url, data={'email': 'foo@bar.com', 'feedback': [q.pk for q in questions]})
        self.assertNoFormErrors(response)
        item = models.OptOut.objects.first()
        self.assertEqual(set(questions), set(item.feedback.all()))

    def test_confirmed(self):
        url = get_opt_out_url("foo@bar.com")
        response = test.Client().post(url, data={'email': 'foo@bar.com'})
        self.assertNoFormErrors(response)
        item = models.OptOut.objects.first()
        self.assertIsNotNone(item)
        self.assertIsNotNone(item.confirmed)

    @override_settings(OUT_OUT_REQUIRE_CONFIRMATION=False)
    def test_not_confirmed(self):
        url = get_opt_out_url("foo@bar.com")
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

