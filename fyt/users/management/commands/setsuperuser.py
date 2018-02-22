from django.core.management.base import BaseCommand

from fyt.users.models import DartmouthUser


class Command(BaseCommand):

    help = 'Give the specified user superuser status'

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
            user.is_superuser = True
            user.save()
            msg = "User '%s' promoted to superuser"
            self.stdout.write(msg % user)
