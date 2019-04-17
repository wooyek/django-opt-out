# coding=utf-8
from django.conf import global_settings
from django.contrib import admin
from import_export.admin import ImportExportMixin

from . import models, resources


@admin.register(models.OptOut)
class OptOutAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = resources.OptOutResource
    list_display = ('ts', 'email', 'ip', 'host', 'ua')
    list_filter = ('ip', 'host', 'ua', 'feedback', 'tags')
    readonly_fields = ('email', 'ts', 'comment', 'ip', 'host', 'ua', 'cookies', 'data', 'ssl')
    date_hierarchy = 'ts'


@admin.register(models.OptOutTag)
class OptOutTagAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = resources.OptOutTagResource
    list_display = ('name', 'description')


@admin.register(models.OptOutFeedbackTranslation)
class OptOutFeedbackTranslationAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = resources.OptOutFeedbackTranslationResource
    list_display = ('text', 'language', 'feedback')


class OptOutFeedbackTranslationInline(admin.TabularInline):
    resource_class = resources.OptOutFeedbackResource
    model = models.OptOutFeedbackTranslation

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "language":
            kwargs['choices'] = global_settings.LANGUAGES
        return super(OptOutFeedbackTranslationInline, self).formfield_for_choice_field(db_field, request, **kwargs)


@admin.register(models.OptOutFeedback)
class OptOutFeedbackAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = resources.OptOutFeedbackResource
    list_display = ('text', 'slug', 'default', 'ordinal', 'all_tag_names')
    list_filter = ('tags', 'default')
    inlines = [OptOutFeedbackTranslationInline]

    def all_tag_names(self, obj):
        return ", ".join((t.name for t in obj.tags.all()))

    all_tag_names.short_description = 'Tag names'

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def queryset(self, request, queryset):
        return queryset.prefech_related('tags')
