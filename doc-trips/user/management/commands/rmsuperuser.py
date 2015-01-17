
from django.core.management.base import BaseCommand

from django.contrib.auth import get_user_model
UserModel = get_user_model()

class Command(BaseCommand):
    
    help = 'Revoke the superuser status of the given users'
    
    def add_arguments(self, parser):
        
        parser.add_argument('net_id')

    def handle(self, *args, **options):
        
        for net_id in args:
            
            try:
                user = UserModel.objects.get(net_id=net_id)
            except UserModel.DoesNotExist:
                err = ("User with net_id '%s' does not exist in the database "
                       "Have them log in first, then retry this command")
                self.stderr.write(err % net_id)
            else:
                user.is_superuser = False
                user.save()
                msg = "Superuser status revoked for User '%s'"
                self.stdout.write(msg % user)
                
