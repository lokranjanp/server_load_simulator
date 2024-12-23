import dotenv
import redis
import mysql.connector
from mysql.connector import pooling
from datetime import datetime
import bcrypt
from otp import *
from otpmail import *

def hash_password(password):
    """
    Hashes a password using bcrypt.

    Args:
        password (str): The plain text password to be hashed.

    Returns:
        tuple: A tuple containing the hashed password and the salt used.
    """
    user_salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), user_salt)
    return hashed_password, user_salt

def create_connection():
    """
    Creates a connection to the MySQL database using credentials from a .env file.

    Returns:
        mysql.connector.connection.MySQLConnection: The database connection object if successful, None otherwise.
    """
    path = ".env"
    try:
        connection_pool = pooling.MySQLConnectionPool(
            host=dotenv.get_key(path, 'DB_HOST'),
            user=dotenv.get_key(path, 'DB_USER'),
            password=dotenv.get_key(path, 'DB_PASSWORD'),
            database=dotenv.get_key(path, 'DB_NAME'),
            pool_size=32
        )
        return connection_pool

    except OSError as e:
        print(f"Database Connection FAILED. Error: {e}")
        return None

def register_user(username, email, password):
    """
    Registers a new user by storing their details in the SQL database.

    Args:
        username (str): The username of the new user.
        email (str): The email address of the new user.
        password (str): The plain text password of the new user.

    Returns:
        bool: True if registration is successful, False otherwise.
    """
    connection = create_connection()
    if connection is None:
        return False

    try:
        cursor = connection.cursor()
        created_at = datetime.now()
        user_otp_secret = pyotp.random_base32()
        hashed_password, user_salt = hash_password(password)
        cursor.execute("INSERT INTO users (username, email, password_hash, otp_secret, created_at ,user_salt) "
                       "VALUES (%s, %s, %s, %s, %s, %s)",
                       (username, email, hashed_password, user_otp_secret, created_at, user_salt))
        connection.commit()
        return True

    except Error as e:
        print(f"Registration Failed. Error: {e}")
        return False

    finally:
        cursor.close()
        connection.close()

def validate_user_2FA(username, otp):
    """
    Validates a user by checking their username and OTP for 2FA.

    Args:
        username (str): The username of the user.
        otp (str): The one-time password for 2FA.

    Returns:
        bool: True if validation is successful, False otherwise.
    """
    r = redis.StrictRedis(host='localhost', port=6379, db=7)

    try:
        if verify_otp(r, username, otp):
            print(f"OTP AUTH successful.")
            return True

    except Error as e:
        print(f"OTP AUTH failed.")
        return False