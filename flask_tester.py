import requests
from register import hash_password
import time

url = "https://127.0.0.1:7019/"
data = {"username": "lokranjan"}
start = time.time()
response = requests.post(url, json=data, verify='/Users/lokranjan/PycharmProjects/workloadsim/cert.pem')
end = time.time()
print(end-start)
print(response.json())
