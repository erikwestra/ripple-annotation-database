""" annotationDatabase.shared.management.commands.recalc_current_annotations

    This Python module implements the "recalc_current_annotations" management
    command for the annotation database.  It allows a system administrator to
    rebuild the CurrentAnnotation table if it gets mucked up.
"""
from django.core.management.base import BaseCommand, CommandError

from annotationDatabase.shared.models import *

#############################################################################

class Command(BaseCommand):
    """ Our "recalc_current_annotations" management command.
    """
    args = None
    help = 'Recalculate the list of CurrentAnnotation records.'

    def handle(self, *args, **kwargs):
        """ Run our management command.
        """
        if len(args) != 0:
            self.stderr.write("This command takes no arguments.")
            return

        CurrentAnnotation.objects.all().delete()

        annotations_to_recalculate = set() # Set of (account, key) tuples.

        for annotation in Annotation.objects.all():
            annotations_to_recalculate.add((annotation.account,
                                            annotation.key))

        for account,key in annotations_to_recalculate:
            cur_value     = None # initially.
            cur_timestamp = None # ditto.
            for annotation in Annotation.objects.filter(account=account,
                                                        key=key):
                if annotation.hidden: continue

                timestamp = annotation.batch.timestamp
                value     = annotation.value

                if cur_value == None:
                    cur_value     = value
                    cur_timestamp = timestamp
                else:
                    if timestamp > cur_timestamp:
                        # Use the most recent value.
                        cur_value     = value
                        cur_timestamp = timestamp

            if cur_value == None:
                try:
                    cur_value = AnnotationValue.objects.get(value="")
                except orm.AnnotationValue.DoesNotExist:
                    cur_value = AnnotationValue()
                    cur_value.value = ""
                    cur_value.save()

            cur_annotation = CurrentAnnotation()
            cur_annotation.account = account
            cur_annotation.key     = key
            cur_annotation.value   = cur_value
            cur_annotation.save()

        self.stdout.write("Done!")

