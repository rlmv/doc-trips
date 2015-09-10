from django.core.management.base import BaseCommand

from django.contrib.auth import get_user_model
UserModel = get_user_model()

class Command(BaseCommand):
    
    help = 'Delete the specified users'
    
    def add_arguments(self, parser):
        
        parser.add_argument('netid')

    def handle(self, *args, **options):
        
        for netid in args:
            
            try:
                user = UserModel.objects.get(netid=netid)
            except UserModel.DoesNotExist:
                err = ("User with netid '%s' does not exist in the database")
                self.stderr.write(err % netid)
            else:
                user.delete()
                msg = "Deleted user '%s'"
                self.stdout.write(msg % user)
                
