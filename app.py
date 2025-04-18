from datetime import datetime
from otp import *
import pyotp
import bcrypt
import random
import time
from flask import Flask, request, jsonify
from pymongo import MongoClient
from otpmail import *
import redis
import psutil
import os

path = ".env"
app = Flask(__name__)

# Database and Redis setup
uri = dotenv.get_key(path, 'MONGO_URI')
client = MongoClient(uri)
db = client["authdata"]
r = redis.StrictRedis(host='localhost', port=dotenv.get_key(path, 'REDIS_PORT'), db=7)
pool = initialize_pool()

@app.route("/otp", methods=['POST'])
def serveotp():
    try:
        data = request.json
        username = data.get('username')
        cursor = db["users"]

        if not username:
            return jsonify({"error": "Username is required"}), 400

        user = cursor.find_one({"username": username})

        if not user:
            return jsonify({"error": "User not found"}), 404

        user_otp_secret = user["otp_secret"]
        user_email = user["email"]

        # Generate OTP
        user_otp = pyotp.TOTP(user_otp_secret).now()
        # cache_otp(r, username, user_otp)

        send_mail(user_email, user_otp, pool)

        return jsonify({"message": f"OTP sent to {user_email}"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def hash_password(password):
    salt = bcrypt.gensalt()
    hashedpw = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashedpw

def random_data_gen(feederstring):
    random.seed(time.time())
    username = feederstring + str(random.randint(1, 1000000))
    hashed_password = hash_password(username)
    domain = random.choice(["gmail.com", "yahoo.com", "outlook.com", "protonmail.com", "example.com"])
    return username, f"{username}@{domain}", hashed_password

@app.route("/register", methods=['POST'])
def register():
    try:
        cursor = db["users"]
        data = request.json
        numrows = data.get('numrows', 1)

        iter = 0
        while iter < numrows:
            feederstring = random.choice(["testmail", "dummymail"])
            username, email, hashed_password = random_data_gen(feederstring)

            try:
                user_otp_secret = pyotp.random_base32()
                created_at = datetime.now()

                # Create and save the user document
                post1 = {"username": username, "email": email, "password": hashed_password,
                         "otp_secret": user_otp_secret, "created_at": created_at}

                cursor.insert_one(post1)

            except Exception as e:
                print(f"Registration Failed. Error: {e}")
                return jsonify({"message": "Registration failed", "error": str(e)}), 500

            iter += 1
        return jsonify({"message": "Users registered successfully"}), 200

    except Exception as e:
        return jsonify({"message": "Registration error", "error": str(e)}), 500

def verify_password(stored_hash, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash)

@app.route("/dummy", methods=['GET'])
def test():
    return jsonify({"message": "Server responding!"}), 200

@app.route("/login", methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    cursor = db["users"]
    user = cursor.find_one({"username": username})

    if not user:
        return jsonify({"error": "User not found"}), 404

    if verify_password(user["password"], password):
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Login Unsuccessful. Please check credentials"}), 401


@app.route('/logs', methods=['GET'])
def get_metrics():
    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        disk_io = psutil.disk_io_counters().write_bytes
        net_io = psutil.net_io_counters()
        net_io_sent = net_io.bytes_sent
        net_io_recv = net_io.bytes_recv

        try:
            load_avg = os.getloadavg()[0]
        except AttributeError:
            load_avg = None

        # Active Connections
        try:
            active_connections = len(psutil.net_connections(kind='inet'))
        except PermissionError:
            active_connections = "Permission Denied"

        metrics = {
            "timestamp": timestamp,
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "disk_io": disk_io,
            "net_io_sent": net_io_sent,
            "net_io_recv": net_io_recv,
            "load_avg": load_avg,
            "active_connections": active_connections
        }
        return jsonify(metrics), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7019)
