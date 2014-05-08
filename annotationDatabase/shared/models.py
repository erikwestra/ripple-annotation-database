""" annotationDatabase.shared.models

    This module defines the shared database modules used by the Ripple
    Annotation Database.
"""
from django.db import models

#############################################################################

class AnnotationKey(models.Model):
    """ A single unique key value used by one or more annotations.
    """
    id  = models.AutoField(primary_key=True)
    key = models.TextField(unique=True, db_index=True)

#############################################################################

class Account(models.Model):
    """ A reference to a Ripple account.
    """
    id      = models.AutoField(primary_key=True)
    address = models.TextField(unique=True, db_index=True)
    # more fields to come...

#############################################################################

class AnnotationBatch(models.Model):
    """ A single batch of uploaded annotations.
    """
    id        = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField()
    user_id   = models.TextField()

#############################################################################

class Annotation(models.Model):
    """ A single uploaded annotation value.
    """
    id        = models.AutoField(primary_key=True)
    batch     = models.ForeignKey(AnnotationBatch)
    account   = models.ForeignKey(Account)
    key       = models.ForeignKey(AnnotationKey)
    value     = models.TextField()
    hidden    = models.BooleanField(default=False)
    hidden_at = models.DateTimeField(null=True)
    hidden_by = models.TextField(null=True)

#############################################################################

class AnnotationTemplate(models.Model):
    """ A single uploaded annotation template.
    """
    id   = models.AutoField(primary_key=True)
    name = models.TextField(unique=True, db_index=True)

#############################################################################

class AnnotationTemplateEntry(models.Model):
    """ A single annotation entry within an annotation template.

        Note that the "choices" field holds the available choices as a JSON
        string.
    """
    id               = models.AutoField(primary_key=True)
    template         = models.ForeignKey(AnnotationTemplate)
    annotation       = models.ForeignKey(AnnotationKey)
    label            = models.TextField()
    type             = models.TextField(choices=[("choice", "choice"),
                                                 ("field",  "field")],
                                        default="field")
    default          = models.TextField(null=True)
    choices          = models.TextField(null=True)
    field_size       = models.IntegerField(null=True)
    field_required   = models.NullBooleanField()
    field_min_length = models.IntegerField(null=True)
    field_max_length = models.IntegerField(null=True)

#############################################################################

class Client(models.Model):
    """ A client system authorized to use the Annotation Database.
    """
    id         = models.AutoField(primary_key=True)
    name       = models.TextField(unique=True, db_index=True)
    auth_token = models.TextField(unique=True, db_index=True)

