# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.db.models import Q
from django.shortcuts import resolve_url
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import ModelFormMixin
from django_powerbank.views import Http403
from django_powerbank.views.auth import AbstractAccessView
from pascal_templates.views import CreateView, DetailView, UpdateView

from . import forms, models
from .signals import opt_out_submitted, opt_out_visited
from .utils import validate_password


class OptOutConfirm(CreateView):
    model = models.OptOut
    template_name = "django_opt_out/OptOut/form.html"
    form_class = forms.OptOutForm

    def email_confirmed(self):
        email = self.request.GET.get('email', None)
        auth = self.request.GET.get('auth', None)
        if email and auth:
            return validate_password(email, auth)

    def get_initial(self):
        return self.request.GET.dict()

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        feedback = form.fields['feedback']
        tags = dict(self.get_tags()).keys()
        feedback.queryset = feedback.queryset.filter(Q(tags__name__in=tags) | Q(tags__isnull=True))
        feedback.initial = list(feedback.queryset.filter(default=True).values_list('pk', flat=True))
        if self.email_confirmed():
            form.instance.confirmed = timezone.now()

        return form

    def get_context_data(self, **kwargs):
        kwargs['tags'] = self.get_tags()
        opt_out_visited.send_robust(self.__class__, view=self, request=self.request, context=kwargs)
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        self.object = form.save()
        self.save_tags()
        opt_out_submitted.send_robust(self.__class__, view=self, request=self.request, opt_out=self.object)
        return super(ModelFormMixin, self).form_valid(form)

    def get_tags(self):
        for name in self.request.GET.getlist('tag', []):
            yield name.split(":", 1) if ":" in name else (name, None)

    def save_tags(self):
        for name, value in self.get_tags():
            tag = models.OptOutTag.objects.filter(name=name).first()
            if tag is None:
                logging.warning("Tag does not exist: %s", name)
                continue
            self.object.tags.create(tag=tag, value=value)

    def get_success_url(self):
        goodbye_view = settings.OPT_OUT_GOODBYE_VIEW or "django_opt_out:OptOutSuccess"
        return resolve_url(goodbye_view, pk=self.object.pk, secret=self.object.secret, email=self.object.email)


class OptOutBase(AbstractAccessView):
    def check_authorization(self, *args, **kwargs):
        # noinspection PyUnresolvedReferences
        item = self.get_object()
        email = self.kwargs['email']
        secret = self.kwargs['secret']
        if item.secret != secret or item.email != email:
            msg = _("Request authentication failed, secret or email is incorrect.")
            raise Http403(msg)


class OptOutSuccess(OptOutBase, DetailView):
    model = models.OptOut
    template_name = "django_opt_out/OptOut/success.html"


class OptOutUpdate(OptOutBase, UpdateView):
    model = models.OptOut
    form_class = forms.OptOutForm
    template_name = "django_opt_out/OptOut/form.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        feedback = form.fields['feedback']
        tags = self.object.tags.all().values_list('tag__pk', flat=True)
        feedback.queryset = feedback.queryset.filter(Q(tags__in=tags) | Q(tags__isnull=True))
        feedback.initial = list(self.object.feedback.all().values_list('pk', flat=True))
        # form.fields['email'].readonly = True
        return form

    def get_success_url(self):
        return resolve_url("django_opt_out:OptOutSuccess", self.object.pk, self.object.secret, self.object.email)
