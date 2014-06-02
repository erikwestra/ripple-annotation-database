""" annotationDatabase.shared.management.commands.migrate_users

    This Django management command migrates the existing public.models.User
    records (and related objects) across to shared.models.User.
"""
from django.core.management.base import BaseCommand, CommandError

from annotationDatabase.shared.models import *
from annotationDatabase.public.models import User    as PublicUser
from annotationDatabase.public.models import Account as PublicAccount

#############################################################################

class Command(BaseCommand):
    """ Our "migrate_users" management command.
    """
    args = None
    help = 'Migrate public.models.User to shared.model.User'

    def handle(self, *args, **kwargs):
        """ Run our management command.
        """
        if len(args) != 0:
            self.stderr.write("This command takes no arguments.")
            return

        # Scan through the PublicUser records, creating any User records which
        # we don't already have.

        users = {} # Maps PublicUser.id to User record.

        for public_user in PublicUser.objects.all():
            try:
                user = User.objects.get(username=public_user.username)
            except User.DoesNotExist:
                user = User()
                user.username      = public_user.username
                user.password_salt = public_user.password_salt
                user.password_hash = public_user.password_hash
                user.blocked       = public_user.blocked
                user.save()

            users[public_user.id] = user

        # Now go through the PublicAccount records, creating any missing
        # Account records.

        for public_account in PublicAccount.objects.all():
            try:
                account = Account.objects.get(address=public_account.address)
                account.owner = users[public_account.owner.id]
                account.save()
            except Account.DoesNotExist:
                account = Account()
                account.address = public_account.address
                account.owner   = users[public_account.owner.id]
                account.save()

        # Finally, delete any Account objects which don't have an owner.

        accounts_to_delete = []
        for account in Account.objects.all():
            if account.owner == None:
                accounts_to_delete.append(account)

        for account in accounts_to_delete:
            account.delete()

        self.stdout.write("Done!")

