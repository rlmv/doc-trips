from django.core.management.base import BaseCommand

from fyt.users.models import DartmouthUser


class Command(BaseCommand):

    help = 'Revoke the superuser status of the given users'

    def add_arguments(self, parser):
        parser.add_argument('netid')

    def handle(self, *args, **options):
        netid = options['netid']

        try:
            user = DartmouthUser.objects.get(netid=netid)
        except DartmouthUser.DoesNotExist:
            err = ("User with netid '%s' does not exist in the database "
                   "Have them log in first, then retry this command")
            self.stderr.write(err % netid)
        else:
            user.is_superuser = False
            user.save()
            msg = "Superuser status revoked for User '%s'"
            self.stdout.write(msg % user)
