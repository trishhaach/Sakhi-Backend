from django.core.management.base import BaseCommand
from pymongo import MongoClient

class Command(BaseCommand):
    help = 'Drops the conflicting index from the MongoDB collection'

    def handle(self, *args, **kwargs):
        client = MongoClient("mongodb+srv://trishachaudhary:FIRSTDECEMBER2002@cluster0.ufh0evp.mongodb.net/sakhiAuthentication?retryWrites=true&w=majority&appName=Cluster0")
        db = client['sakhiAuthentication']
        collection = db['django_session']
        indexes = collection.index_information()

        for index_name in indexes:
            print(index_name)

        # Assuming the conflicting index name is 'django_session_expire_date_a5c62663'
        collection.drop_index('django_session_expire_date_a5c62663')
        self.stdout.write(self.style.SUCCESS('Successfully dropped the conflicting index.'))
