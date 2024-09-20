from mongoengine import Document, fields
from django.contrib.auth.hashers import make_password, check_password

class User(Document):
    email = fields.EmailField(required=True, unique=True)
    name = fields.StringField(max_length=255, required=True)
    password = fields.StringField(required=True)
    is_active = fields.BooleanField(default=True)
    is_admin = fields.BooleanField(default=False)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    @property
    def is_staff(self):
        return self.is_admin

    meta = {
        'collection': 'user',
        'indexes': [
            {'fields': ['email'], 'unique': True}
        ]
    }
