from mongoengine import Document, StringField, EmailField, ListField, ReferenceField, IntField, DateTimeField
from datetime import datetime


class User(Document):
    username = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    password_hash = StringField(required=True)
    otp_secret = StringField()
    created_at = DateTimeField(default=datetime.now)
    meta = {'timestamps': True}

    def to_dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "otp_secret": self.otp_secret,
            "created_at": self.created_at,
        }