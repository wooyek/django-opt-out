# coding=utf-8
import logging
from pathlib import Path

import tablib
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _

from ... import models, resources

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Imports default opt-out feedback options to empty database'

    data_files = (
        ("tags.csv", resources.OptOutTagResource),
        ("feedback.csv", resources.OptOutFeedbackResource),
        ("feedback-translations.csv", resources.OptOutFeedbackTranslationResource),
    )

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', dest='force', default=False, help='Overwrite existing data')
        parser.add_argument('--on-empty', action='store_true', dest='on_empty', default=False, help='Only if database is emtpy')

    def handle(self, *args, **options):
        if not options['force']:
            try:
                assert models.OptOutTag.objects.count() == 0
                assert models.OptOutFeedback.objects.count() == 0
                assert models.OptOutFeedbackTranslation.objects.count() == 0
            except AssertionError as ex:
                if options['on_empty']:
                    log.info("Database is not empty. Ignoring import.")
                    return
                raise ex
        self.import_all()

    def import_all(self):
        for name, resource in self.data_files:
            self.import_data_file(name, resource)

    @staticmethod
    def import_data_file(name, resource):
        data_file = Path(__file__).parent / name
        log.debug("Looking data file: %s", str(data_file))
        with (data_file).open(encoding='UTF-8') as data:
            dataset = tablib.Dataset().load(data.read(), format='csv')

        if dataset.width < 1:
            raise ValidationError(_("Data set has no columns"))
        if dataset.height < 1:
            raise ValidationError(_("Data set has no rows"))

        # log.debug("Trying dryrun...")
        # OrganizationLocationResource().import_data(dataset, dry_run=True, raise_errors=True)
        log.debug(_('Trying to import {}').format(name))
        result = resource().import_data(dataset, dry_run=False, raise_errors=True)
        log.info(_('Imported {} rows from {}').format(result.total_rows, name))
