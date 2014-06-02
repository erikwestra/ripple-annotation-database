""" annotationDatabase.shared.models

    This module defines the shared database modules used by the Ripple
    Annotation Database.
"""
import hashlib
import uuid

from django.db import models

#############################################################################

class User(models.Model):
    """ A signed-up user of the public interface.
    """
    id            = models.AutoField(primary_key=True)
    username      = models.TextField(unique=True, db_index=True)
    password_salt = models.TextField()
    password_hash = models.TextField()
    blocked       = models.BooleanField(default=False)


    def set_password(self, password):
        """ Encrypt the given password and store it into this User object.
        """
        self.password_salt = uuid.uuid4().hex
        self.password_hash = hashlib.md5(password +
                                         self.password_salt).hexdigest()


    def is_password_correct(self, password):
        """ Return True if and only if the given password is correct.
        """
        hash = hashlib.md5(password + self.password_salt).hexdigest()
        return (hash == self.password_hash)

#############################################################################

class AnnotationKey(models.Model):
    """ A single unique annotation key used by one or more annotations.
    """
    id  = models.AutoField(primary_key=True)
    key = models.TextField(unique=True, db_index=True)

#############################################################################

class AnnotationValue(models.Model):
    """ A single unique annotation value used by one or more annotations.
    """
    id    = models.AutoField(primary_key=True)
    value = models.TextField(unique=True, db_index=True)

#############################################################################

class Account(models.Model):
    """ A reference to a Ripple account.
    """
    id      = models.AutoField(primary_key=True)
    address = models.TextField(unique=True, db_index=True)
    owner   = models.ForeignKey(User, null=True)

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

        Note that the Annotation records are never deleted or overwritten; they
        provide an audit trail of the changes made to the annotation values
        over time.
    """
    id        = models.AutoField(primary_key=True)
    batch     = models.ForeignKey(AnnotationBatch)
    account   = models.ForeignKey(Account)
    key       = models.ForeignKey(AnnotationKey)
    value     = models.ForeignKey(AnnotationValue, null=True)
    hidden    = models.BooleanField(default=False)
    hidden_at = models.DateTimeField(null=True)
    hidden_by = models.TextField(null=True)

#############################################################################

class CurrentAnnotation(models.Model):
    """ A single annotation currently in use.

        There is one and only one CurrentAnnotation record for every
        combination of account and annotation key.  This is distinct from
        the Annotation record, which holds annotations which may once have
        applied but have now been overwritten.
    """
    id      = models.AutoField(primary_key=True)
    account = models.ForeignKey(Account)
    key     = models.ForeignKey(AnnotationKey)
    value   = models.ForeignKey(AnnotationValue)

    class Meta:
        unique_together = [
            ["account", "key"],
        ]

        index_together = [
            ["key", "value"],
        ]

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

#############################################################################

class Session(models.Model):
    """ An active session within the Authentication app.
    """
    id            = models.AutoField(primary_key=True)
    session_token = models.TextField()
    user          = models.ForeignKey(User)
    last_access   = models.DateTimeField()

