import time
from register import *
import mysql.connector
from mysql.connector import *
from register import *
import random
import string
import pyotp

def data_inserter(numrows):
    connection = create_connection()

    if connection is None:
        return False

    iter = 0
    while iter < numrows:
        feederstring = random.choice(["testmail", "dummymail"])
        username, email, hashed_password, user_salt = random_data_gen(feederstring)

        try:
            cursor = connection.cursor()
            created_at = datetime.now()
            user_otp_secret = pyotp.random_base32()
            cursor.execute("INSERT INTO users (username, email, password_hash, otp_secret, created_at ,user_salt) "
                           "VALUES (%s, %s, %s, %s, %s, %s)",
                           (username, email, hashed_password, user_otp_secret, created_at, user_salt))
            connection.commit()
            print(f"current row : {iter}")

        except Error as e:
            print(f"Registration Failed. Error: {e}")
            return False

        iter += 1

    return True

def random_data_gen(feederstring):
    """
    Generates a realistic random email using regex patterns.
    Returns:
        str: A valid email address.
    """
    random.seed(time.time())
    username = feederstring+ str(random.randint(1, 1000000))
    hashpassword, usersalt = hash_password(username)
    domain = random.choice(["gmail.com", "yahoo.com", "outlook.com", "protonmail.com", "example.com"])
    return username, f"{username}@{domain}", hashpassword, usersalt
