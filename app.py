from flask import Flask, request, jsonify
import redis
from data import data_inserter
from otp import generate_otp
from otpmail import send_mail, initialize_pool
from data import create_connection, cache_otp
import bcrypt
import dotenv

path = ".env"
app = Flask(__name__)

# Database and Redis setup
connection_pool = create_connection()
connection = connection_pool.get_connection()
cursor = connection.cursor()
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


@app.route("/register", methods=['POST'])
def register():
    try:
        # # Assuming data_inserter handles registration logic
        # data = request.json  # Extract the registration data from the request
        # if not data:
        #     return jsonify({"error": "Invalid data"}), 400
        data = request.json
        numrows = data.get('numrows')
        data_inserter(numrows)  # Pass the registration data to your function
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

        if connection is None:
            return False

    except Exception as e:
            return jsonify({"error": str(e)}), 300

    try:
        cursor.execute("SELECT u.password_hash, u.user_salt FROM users u WHERE u.username = %s", (username,))
        user = cursor.fetchone()

        if user:
            usersalt, stored_hash = user # Extract usersalt and stored hash
            stored_hash = stored_hash.encode('utf-8') if isinstance(stored_hash, str) else stored_hash
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                print("Login successful!")
            else:
                print("Invalid username or password.")
        else:
            print("User does not exist.")

    except Exception as e:
            return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7019, debug=True, ssl_context=('cert.pem', 'key.pem'))
