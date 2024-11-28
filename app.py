from flask import Flask, request, jsonify
import mysql.connector
import redis
from data import data_inserter
from otp import generate_otp
from otpmail import send_mail
from data import create_connection, cache_otp, validate_user

app = Flask(__name__)

# Database and Redis setup
dbconnect = create_connection()
cursor = dbconnect.cursor()
r = redis.StrictRedis(host='localhost', port=6379, db=7)

@app.route("/otp", methods=['POST'])
def serveotp():
    try:
        # Extracting username from the JSON body
        data = request.json
        username = data.get('username')

        if not username:
            return jsonify({"error": "Username is required"}), 400

        # Fetching user details from the database
        cursor.execute("SELECT otp_secret, email FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"error": "User not found"}), 404

        user_secret, user_email = result
        user_otp = generate_otp(user_secret)

        # Cache the OTP in Redis and send via email
        cache_otp(r, username, user_otp)
        send_mail(user_email, user_otp)

        return jsonify({"message": f"OTP sent to {user_email}"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/register", methods=['POST'])
def register():
    try:
        # Assuming data_inserter handles registration logic
        data = request.json  # Extract the registration data from the request
        if not data:
            return jsonify({"error": "Invalid data"}), 400

        data_inserter(data)  # Pass the registration data to your function
        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/login", methods=['POST'])
def login():
    try:
        # Extracting login credentials
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        # Validate the user
        is_valid = validate_user(dbconnect, username, password)
        if is_valid:
            return jsonify({"message": "Login successful"}), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7019, debug=True)
