# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django_powerbank.db.models.base import BaseModel
from django_powerbank.db.models.fields import AutoSlugField, JSONField, SecretField


class OptOutTag(BaseModel):
    name = models.CharField(verbose_name=_('tag name'), max_length=30)
    description = models.CharField(verbose_name=_('description'), max_length=250, default='')

    class Meta:
        default_related_name = "tag_names"
        verbose_name = _('tag')
        verbose_name_plural = _('tags')

    def __str__(self):
        return self.name


class OptOutFeedback(BaseModel):
    text = models.CharField(verbose_name=_('text'), max_length=250)
    slug = AutoSlugField(source_field='text', keep_existing=True, max_length=30, unique=True)
    default = models.BooleanField(verbose_name=_('checked by default'), default=False)
    ordinal = models.PositiveIntegerField(verbose_name=_('ordinal'), default=0)
    tags = models.ManyToManyField(OptOutTag, verbose_name=_('tags'), blank=True)

    class Meta:
        default_related_name = "feedback"
        verbose_name = _('feedback option')
        verbose_name_plural = _('feedback options')

    def __str__(self):
        return self.text

    def trans(self, language=None):
        if language is None:
            language = translation.get_language()
        label = OptOutFeedbackTranslation.objects.filter(feedback=self, language=language).first() or self
        return label.text


class OptOutFeedbackTranslation(BaseModel):
    feedback = models.ForeignKey(OptOutFeedback, on_delete=models.CASCADE)
    language = models.CharField(max_length=5, choices=settings.LANGUAGES)
    text = models.CharField(verbose_name=_('question'), max_length=250)

    class Meta:
        default_related_name = 'translations'
        unique_together = (('feedback', 'text'), ('feedback', 'language'))
        verbose_name = _('feedback option translation')
        verbose_name_plural = _('feedback options translations')


class OptOut(BaseModel):
    email = models.EmailField(verbose_name=_('email'))
    ts = models.DateTimeField(verbose_name=_('update timestamp'), auto_now=True)
    confirmed = models.DateTimeField(verbose_name=_('confirmation timestamp'), null=True, blank=True)
    data = JSONField(verbose_name=_('extra data'), null=True, blank=True)
    comment = models.TextField(verbose_name=_('comment'), null=True, blank=True)
    feedback = models.ManyToManyField(OptOutFeedback, verbose_name=_('feedback'))
    secret = SecretField(source_field="email", max_length=200)

    # Signature elements
    ssl = models.NullBooleanField()
    host = models.CharField(max_length=200, null=True, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    ua = models.CharField(max_length=200, null=True, blank=True)
    cookies = models.TextField(null=True, blank=True)

    class Meta:
        default_related_name = "out_outs"
        verbose_name = _('opt out')
        verbose_name_plural = _('oup outs')


class OptOutTagValue(BaseModel):
    opt_out = models.ForeignKey(OptOut, on_delete=models.CASCADE)
    tag = models.ForeignKey(OptOutTag, on_delete=models.PROTECT)
    value = models.CharField(verbose_name=_('tag value'), max_length=80, db_index=True, null=True, blank=True)

    class Meta:
        default_related_name = "tags"
        verbose_name = _('tag')
        verbose_name_plural = _('tags')

    def __str__(self):
        return "OptOut-{}:{}:{}".format(self.opt_out_id, self.tag.name, self.value)
