from django.core.management.base import BaseCommand

from fyt.users.models import DartmouthUser


class Command(BaseCommand):

    help = 'Delete the specified users'

    def add_arguments(self, parser):
        parser.add_argument('netid')

    def handle(self, *args, **options):
        netid = options['netid']

        try:
            user = DartmouthUser.objects.get(netid=netid)
        except DartmouthUser.DoesNotExist:
            err = "User with netid '%s' does not exist in the database"
            self.stderr.write(err % netid)
        else:
            user.delete()
            msg = "Deleted user '%s'"
            self.stdout.write(msg % user)
