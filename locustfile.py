from locust import HttpUser, task, between
import time
import csv
import random

def load_usernames_from_csv(filepath):
    with open(filepath, "r") as file:
        reader = csv.DictReader(file)
        return [row["username"] for row in reader]

USERNAMES = load_usernames_from_csv("userdump.csv")

class SimulateFlaskApp(HttpUser):
    wait_time = between(1, 3)
    host = "https://127.0.0.1:7019"  # Add your host here
    random.seed(time.time())

    @task(1)
    def test_otpgen(self):
        random.seed(time.time())
        data = {"username": random.choice(USERNAMES)}
        cert_path = "/Users/lokranjan/PycharmProjects/workloadsim/cert.pem"
        start_time = time.time()
        with self.client.post(
            "/otp",  # Endpoint relative to the host
            json=data,
            verify=cert_path,
            catch_response=True
        ) as response:
            end_time = time.time()
            if response.status_code == 200:
                response.success()
                print(f"Serve OTP Request took {end_time - start_time:.2f} seconds")
            else:
                response.failure(f"Failed with status code {response.status_code}: {response.text}")

    @task(3)
    def test_login(self):
        random.seed(time.time())
        cert_path = "/Users/lokranjan/PycharmProjects/workloadsim/cert.pem"
        self.username = random.choice(USERNAMES)
        data = {"username": self.username, "password":self.username}
        start_time = time.time()
        with self.client.post(
            "/login", json=data,
            verify=cert_path,
            catch_response=True
        ) as response:
            end_time = time.time()
            if response.status_code == 200:
                response.success()
                print(f"Login Request took {end_time - start_time:.2f} seconds")
            else:
                response.failure(f"Failed with status code {response.status_code}: {response.text}")

    @task(1)
    def test_register(self):
        random.seed(time.time())
        cert_path = "/Users/lokranjan/PycharmProjects/workloadsim/cert.pem"
        data = {"numrows": 1}
        start_time = time.time()
        with self.client.post(
            "/register", json=data,
            verify=cert_path,
            catch_response=True
        ) as response:
            end_time = time.time()
            if response.status_code == 201:
                response.success()
                print(f"Register Request took {end_time - start_time:.2f} seconds")
            else:
                response.failure(f"Failed with status code {response.status_code}: {response.text}")

