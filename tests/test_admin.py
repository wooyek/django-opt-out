# coding=utf-8
from django.test import TestCase

from django_opt_out import admin, factories, models


class OptOutFeedbackAdminTests(TestCase):
    def test_all_tag_names(self):
        item = factories.OptOutFeedbackFactory()
        item.tags.create(name="a")
        item.tags.create(name="b")
        item.tags.create(name="c")
        self.assertEqual("a, b, c", admin.OptOutFeedbackAdmin(models.OptOutFeedback, None).all_tag_names(item))
