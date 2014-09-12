
from django.core.management.base import BaseCommand

from django.contrib.auth import get_user_model
UserModel = get_user_model()

class Command(BaseCommand):
    
    help = 'Give the specified user superuser status'
    
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
                user.is_superuser = True
                user.is_staff = True
                user.save()
                msg = "User '%s' promoted to superuser"
                self.stdout.write(msg % user)
                



            
        
