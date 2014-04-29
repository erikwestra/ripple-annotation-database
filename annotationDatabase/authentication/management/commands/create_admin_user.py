""" authentication.management.commands.create_admin_user

    This Python module implements the "create_admin_user" management command
    for the Authentication app.  It allows a system administrator to create the
    initial admin user for the system.
"""
import getpass

from django.core.management.base import BaseCommand, CommandError

from ...       import app_settings
from ...models import *

#############################################################################

class Command(BaseCommand):
    """ Our "create_admin_user" management command.
    """
    args = 'username'
    help = 'Create an initial admin user within the Authentication app.'

    def handle(self, *args, **kwargs):
        """ Run our management command.
        """
        if len(args) != 1:
            self.stderr.write("Missing required 'username' parameter.")
            return

        username = args[0]

        try:
            existing_user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            existing_user = None

        if existing_user != None:
            self.stderr.write("There is already a user with that username.")
            return

        pass1 = getpass.getpass("Enter password: ")
        if pass1 == "":
            self.stderr.write("You must enter a password for this user.")
            return

        pass2 = getpass.getpass("Re-enter password:")
        if pass1 != pass2:
            self.stderr.write("Entered passwords do not match.")
            return

        user = User()
        user.username = username
        user.type     = app_settings.ADMIN_USER_TYPE
        user.set_password(pass1)
        user.save()

        self.stdout.write("User created.")

