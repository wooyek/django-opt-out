# coding=utf-8
from django.contrib.admin import AdminSite
from django.test import TestCase

from django_opt_out import admin, factories, models


class OptOutFeedbackAdminTests(TestCase):
    def test_all_tag_names(self):
        item = factories.OptOutFeedbackFactory()
        item.tags.create(name="a")
        item.tags.create(name="b")
        item.tags.create(name="c")
        self.assertEqual("a, b, c", admin.OptOutFeedbackAdmin(models.OptOutFeedback, None).all_tag_names(item))

    def test_queryset(self):
        tags = factories.OptOutTagFactory.create_batch(10)
        factories.OptOutFeedbackFactory(tags=tags)
        ma = admin.OptOutFeedbackAdmin(models.OptOutFeedback, AdminSite)
        qry = ma.get_queryset(None)
        self.assertNumQueries(1, lambda: list(qry))
