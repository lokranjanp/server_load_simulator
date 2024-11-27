import mysql.connector
from mysql.connector import *
from register import *
import random
import string

def random_email_gen(feedstring):
    domain = random.choice(["gmail.com", "yahoo.com", "outlook.com", "protonmail.com", "example.com"])

# def data_inserter(num):
#     connection = create_connection()
#
#     if connection is None:
#         return False
#
#     try:
#         cursor = connection.cursor()
#         created_at = datetime.now()
#         user_otp_secret = pyotp.random_base32()
#         hashed_password, user_salt = hash_password(password)
#         cursor.execute("INSERT INTO users (username, email, password_hash, otp_secret, created_at ,user_salt) "
#                        "VALUES (%s, %s, %s, %s, %s, %s)",
#                        (username, email, hashed_password, user_otp_secret, created_at, user_salt))
#         connection.commit()
#         return True
#
#     except Error as e:
#         print(f"Registration Failed. Error: {e}")
#         return False

def create_random_email():
    """
    Generates a realistic random email using regex patterns.
    Returns:
        str: A valid email address.
    """
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 10)))
    domain = random.choice(["gmail.com", "yahoo.com", "outlook.com", "protonmail.com", "example.com"])
    return f"{username}@{domain}"

iter = 0
while iter < 10000:
    print(create_random_email())
    iter += 1

