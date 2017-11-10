# coding=utf-8
import logging
from pathlib import Path

import tablib
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _

from ... import models, resources


class Command(BaseCommand):
    help = 'Imports default opt-out feedback options to empty database'

    data_files = (
        ("tags.csv", resources.OptOutTagResource),
        ("feedback.csv", resources.OptOutFeedbackResource),
        ("feedback-translations.csv", resources.OptOutFeedbackTranslationResource),
    )

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', dest='force', default=False, help='Overwrite existing data')

    def handle(self, *args, **options):
        if not options['force']:
            assert models.OptOutTag.objects.count() == 0
            assert models.OptOutFeedback.objects.count() == 0
            assert models.OptOutFeedbackTranslation.objects.count() == 0
        self.import_all()

    def import_all(self):
        for name, resource in self.data_files:
            self.import_data_file(name, resource)

    @staticmethod
    def import_data_file(name, resource):
        data_file = Path(__file__).parent / name
        logging.debug("Looking data file: %s", str(data_file))
        with (data_file).open(encoding='UTF-8') as data:
            dataset = tablib.Dataset().load(data.read(), format='csv')

        if dataset.width < 1:
            raise ValidationError(_("Data set has no columns"))
        if dataset.height < 1:
            raise ValidationError(_("Data set has no rows"))

        # logging.debug("Trying dryrun...")
        # OrganizationLocationResource().import_data(dataset, dry_run=True, raise_errors=True)
        logging.debug(_('Trying to import {}').format(name))
        result = resource().import_data(dataset, dry_run=False, raise_errors=True)
        logging.info(_('Imported {} rows from {}').format(result.total_rows, name))
