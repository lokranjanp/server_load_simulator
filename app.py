from flask import Flask, request, jsonify
import redis
import random
import pyotp
import datetime
import time
from otp import generate_otp
from otpmail import send_mail, initialize_pool
from data import create_connection, cache_otp
import bcrypt
import dotenv
from register import *

path = ".env"
app = Flask(__name__)

# Database and Redis setup
connection_pool = create_connection()
r = redis.StrictRedis(host='localhost', port=dotenv.get_key(path, 'REDIS_PORT'), db=7)
pool = initialize_pool()

@app.route("/otp", methods=['POST'])
def serveotp():
    try:
        # Extracting username from the JSON body
        data = request.json
        username = data.get('username')

        if not username:
            return jsonify({"error": "Username is required"}), 400

        connection = connection_pool.get_connection()
        cursor = connection.cursor()

        # Fetching user details from the database
        cursor.execute("SELECT otp_secret, email FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"error": "User not found"}), 404

        user_secret, user_email = result
        user_otp = generate_otp(user_secret)

        # Cache the OTP in Redis and send via email
        cache_otp(r, username, user_otp)
        send_mail(user_email, user_otp, pool)

        return jsonify({"message": f"OTP sent to {user_email}"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def random_data_gen(feederstring):
    """
    Generates a realistic random email using regex patterns.
    Returns:
        str: A valid email address.
    """
    random.seed(time.time())
    username = feederstring + str(random.randint(1, 1000000))
    hashpassword, usersalt = hash_password(username)
    domain = random.choice(["gmail.com", "yahoo.com", "outlook.com", "protonmail.com", "example.com"])
    return username, f"{username}@{domain}", hashpassword, usersalt

@app.route("/register", methods=['POST'])
def register():
    try:
        data = request.json
        numrows = data.get('numrows')
        connection = connection_pool.get_connection()

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

            except Exception as e:
                print(f"Registration Failed. Error: {e}")
                return False

            iter += 1
        return jsonify({"message": "User registered successfully"}), 200

    except Exception as e:
        return jsonify({"Registration error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
            connection.close()


@app.route("/login", methods=['POST'])
def login():
    try:
        # Extracting login credentials
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        connection = connection_pool.get_connection()

        if connection is None:
            return False

    except Exception as e:
        return jsonify({"DB Connection error": str(e)}), 300

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT u.password_hash, u.user_salt FROM users u WHERE u.username = %s", (username,))
        user = cursor.fetchone()

        if user:
            usersalt, stored_hash = user  #Extract user salt and stored hash
            stored_hash = stored_hash.encode('utf-8') if isinstance(stored_hash, str) else stored_hash
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                print("Login successful!")
            else:
                return "Invalid username or password."
        else:
            return "User does not exist."

    except Exception as e:
        return jsonify({"DB Query error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
            connection.close()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7019, ssl_context=('cert.pem', 'key.pem'))
