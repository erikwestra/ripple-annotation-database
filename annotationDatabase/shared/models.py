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

class Client(models.Model):
    """ A client system authorized to use the Annotation Database.
    """
    id         = models.AutoField(primary_key=True)
    name       = models.TextField(unique=True, db_index=True)
    auth_token = models.TextField(unique=True, db_index=True)

