""" annotationDatabase.public.models

    This file contains the Django models used by the Annotation Database's
    "public" application.
"""
import hashlib
import uuid

from django.db import models

#############################################################################

class User(models.Model):
    """ An authenticated user of the public interface.
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

class Account(models.Model):
    """ A single Ripple account owned by an authenticated user.
    """
    id      = models.AutoField(primary_key=True)
    address = models.TextField(unique=True, db_index=True)
    owner   = models.ForeignKey(User)

#############################################################################

class Session(models.Model):
    """ An active session within the Authentication app.
    """
    id            = models.AutoField(primary_key=True)
    session_token = models.TextField()
    user          = models.ForeignKey(User)
    last_access   = models.DateTimeField()

