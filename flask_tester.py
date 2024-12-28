import requests
import random
import time

random.seed(time.time())
# url = "http://127.0.0.1:7019/register"
# data = {"numrows" : 89}
# start = time.time()
# response = requests.post(url, json=data)
# print(response)
# end = time.time()
# print(end-start)

url = "http://127.0.0.1:7019/login"
data = {"username": "lokranjan", "password": "loki2003"}
start = time.time()
response = requests.post(url, json=data)
print(response)
end = time.time()
print(end-start)

