from mongoengine import Document, fields
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime

class User(Document):
    email = fields.EmailField(required=True, unique=True)
    name = fields.StringField(max_length=255, required=True)
    password = fields.StringField(required=True)
    is_active = fields.BooleanField(default=True)
    is_admin = fields.BooleanField(default=False)
    last_login = fields.DateTimeField(default=datetime.now)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    def get_email_field_name(self):
        return 'email'

    @property
    def is_staff(self):
        return self.is_admin
    
    @property
    def is_authenticated(self):
        return True

    meta = {
        'collection': 'user',
        'indexes': [
            {'fields': ['email'], 'unique': True}
        ]
    }