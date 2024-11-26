from otp import *
from otpmail import *
from register import *
from sessions import *

path = ".env"
r = redis.StrictRedis(host=dotenv.get_key(path, "REDIS_HOST"),
                      port=dotenv.get_key(path, "REDIS_PORT"),
                      db=dotenv.get_key(path, "REDIS_DB"))

genotp = generate_otp("Loki")
print(genotp)
print(cache_otp(r, "pookie", genotp))
