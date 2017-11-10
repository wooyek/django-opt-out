# coding=utf-8
from import_export import resources, widgets

from . import models


class OptOutTagResource(resources.ModelResource):
    class Meta:
        model = models.OptOutTag
        export_order = ('name',)
        fields = (
            'id',
            'name',
        )


class OptOutFeedbackResource(resources.ModelResource):
    tags = resources.Field(attribute='tags', column_name='tags', widget=widgets.ManyToManyWidget(models.OptOutTag, field='name'))

    class Meta:
        model = models.OptOutFeedback
        export_order = ('text',)
        fields = (
            'id',
            'text',
            'slug',
            'default',
            'ordinal',
            'tags',
        )


class OptOutFeedbackTranslationResource(resources.ModelResource):
    feedback = resources.Field(attribute='feedback', column_name='feedback', widget=widgets.ForeignKeyWidget(models.OptOutFeedback, field='slug'))

    class Meta:
        model = models.OptOutFeedbackTranslation
        export_order = ('text',)
        fields = (
            'id',
            'feedback',
            'text',
            'language',
        )


class OptOutResource(resources.ModelResource):
    feedback = resources.Field(attribute='tags', column_name='tags', widget=widgets.ManyToManyWidget(models.OptOutFeedback, field='slug'))

    class Meta:
        model = models.OptOut
        export_order = ('ts',)
        fields = (
            'email',
            'ts',
            'confirmed',
            'data',
            'comment',
            'feedback',
            'secret',
            'ssl',
            'ip',
            'ua',
            'cookies',
        )


class OptOutTagValueResource(resources.ModelResource):
    opt_out = resources.Field(attribute='tags', column_name='tags', widget=widgets.ForeignKeyWidget(models.OptOut))
    tag = resources.Field(attribute='tags', column_name='tags', widget=widgets.ForeignKeyWidget(models.OptOutTag, 'name'))

    class Meta:
        model = models.OptOutTagValue
        export_order = ('text',)
        fields = (
            'opt_out',
            'tag',
            'value',
        )
