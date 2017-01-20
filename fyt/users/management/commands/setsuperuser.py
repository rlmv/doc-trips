
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


UserModel = get_user_model()


class Command(BaseCommand):

    help = 'Give the specified user superuser status'

    def add_arguments(self, parser):
        parser.add_argument('netid')

    def handle(self, *args, **options):
        netid = options['netid']

        try:
            user = UserModel.objects.get(netid=netid)
        except UserModel.DoesNotExist:
            err = ("User with netid '%s' does not exist in the database "
                   "Have them log in first, then retry this command")
            self.stderr.write(err % netid)
        else:
            user.is_superuser = True
            user.save()
            msg = "User '%s' promoted to superuser"
            self.stdout.write(msg % user)
