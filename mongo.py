from model import User
from pymongo.mongo_client import MongoClient
from datetime import datetime
import pyotp
import bcrypt

uri = "mongodb+srv://lokranjan03:loki2003@cluster0.klgxr.mongodb.net/authdata?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client["authdata"]
cursor = db["users"]

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

def verify_password(stored_hash, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash)

# Example: Verify during login
stored_user = cursor.find_one({"username": "testmail486804"})
if verify_password(stored_user["password"], "testmail486804"):
    print("Login successful!")
else:
    print("Invalid password!")

# username = StringField(required=True, unique=True)
#     email = EmailField(required=True, unique=True)
#     password_hash = StringField(required=True)
#     otp_secret = StringField()
#     user_salt = StringField()
#     created_at = DateTimeField(default=datetime.now)