import requests
import random
import csv
from register import hash_password
import time

def load_usernames_from_csv(filepath):
    with open(filepath, "r") as file:
        reader = csv.DictReader(file)
        return [row["username"] for row in reader]

USERNAMES = load_usernames_from_csv("userdump.csv")

iter = 0

while iter<1:
    random.seed(time.time())
    url = "https://127.0.0.1:7019/otp"
    data = {"username": random.choice(USERNAMES)}
    print(data)
    start = time.time()
    response = requests.post(url, json=data, verify='/Users/lokranjan/PycharmProjects/workloadsim/cert.pem')
    end = time.time()
    print(iter, end-start)
    iter += 1

