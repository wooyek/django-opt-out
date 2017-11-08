# coding=utf-8
from django.contrib import admin
from import_export.admin import ImportExportMixin

from . import models


@admin.register(models.OptOut)
class OptOutAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('ts', 'email', 'ip', 'host', 'ua')
    list_filter = ('ip', 'host', 'ua', 'feedback', 'tags')
    readonly_fields = ('email', 'ts', 'comment', 'ip', 'host', 'ua', 'cookies', 'data', 'ssl')
    date_hierarchy = 'ts'


@admin.register(models.OptOutTag)
class OptOutQuestionAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('name',)


@admin.register(models.OptOutFeedback)
class OptOutFeedbackAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('question', 'all_tag_names')
    list_filter = ('tags',)

    def all_tag_names(self, obj):
        return ", ".join((t.name for t in obj.tags.all()))

    all_tag_names.short_description = 'Tag names'

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def queryset(self, request, queryset):
        return queryset.prefech_related('tags')
