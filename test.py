from otp import *
from otpmail import *
from register import *

path = ".env"
r = redis.StrictRedis(host=dotenv.get_key(path, "REDIS_HOST"),
                      port=dotenv.get_key(path, "REDIS_PORT"),
                      db=dotenv.get_key(path, "REDIS_DB"))

genotp = generate_otp("Loki")
username_input = input("Enter username : ")
print(genotp)
cache_otp(r, username_input, genotp)
user_otp_input = str(input("Enter OTP : "))
print(validate_user_2FA(username_input, user_otp_input))
