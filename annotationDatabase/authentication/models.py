""" authentication.models

    This file contains the Django models used by the Authentication app.
"""
import hashlib
import uuid

from django.db import models

#############################################################################

class User(models.Model):
    """ A user within the Authentication app.
    """
    id        = models.AutoField(primary_key=True)
    username  = models.CharField(max_length=255, db_index=True, unique=True)
    pass_salt = models.TextField()
    pass_hash = models.TextField()
    type      = models.TextField()


    def set_password(self, password):
        """ Encrypt the given password and store it into this User object.
        """
        self.pass_salt = uuid.uuid4().hex
        self.pass_hash = hashlib.md5(password + self.pass_salt).hexdigest()


    def is_password_correct(self, password):
        """ Return True if and only if the given password is correct.
        """
        hash = hashlib.md5(password + self.pass_salt).hexdigest()
        return (hash == self.pass_hash)

#############################################################################

class Session(models.Model):
    """ An active session within the Authentication app.
    """
    id            = models.AutoField(primary_key=True)
    session_token = models.TextField()
    user          = models.ForeignKey(User)
    last_access   = models.DateTimeField()

