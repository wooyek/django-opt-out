# coding=utf-8
from __future__ import unicode_literals

from django.test import TestCase
from django.utils import translation

from django_opt_out import factories, forms


class OptOutFormTests(TestCase):

    def test_translated_feedback(self):
        feedback = factories.OptOutFeedbackFactory()
        text = 'Zażółć gęślą jaźń'
        feedback.translations.create(text=text, language='pl')
        self.assertEqual('en-us', translation.get_language())
        with translation.override('pl'):
            form = forms.OptOutForm()
            self.assertEqual([(1, text)], list(form.fields['feedback'].choices))
