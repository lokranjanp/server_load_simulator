from locust import HttpUser, task, between
import time
import csv
import random
import csv
import time
import psutil
import os

def load_usernames_from_csv(filepath):
    with open(filepath, "r") as file:
        reader = csv.DictReader(file)
        return [row["Username"] for row in reader]

USERNAMES = load_usernames_from_csv("usernames.csv")


# File to store the metrics
csv_file = "server_metrics.csv"

# Write headers to CSV
with open(csv_file, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["timestamp", "cpu_percent", "memory_percent", "load_avg", "active_connections"])

# Function to log metrics
def log_metrics():
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_percent = psutil.virtual_memory().percent
    load_avg = os.getloadavg()[0]
    active_connections = len(psutil.net_connections(kind='inet'))

    try:
        with open(csv_file, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, cpu_percent, memory_percent, load_avg, active_connections])
        print(f"[{timestamp}] Logged metrics to {csv_file}")
    except Exception as e:
        print(f"[Error] Failed to write to CSV: {e}")


class SimulateFlaskApp(HttpUser):
    wait_time = between(1, 3)
    host = "http://0.0.0.0:7019"  # Add your host here
    random.seed(time.time())

    @task(1)
    def test_otpgen(self):
        log_metrics()
        random.seed(time.time())
        data = {"username": random.choice(USERNAMES)}
        start_time = time.time()
        print(data)
        with self.client.post(
            "/otp",  # Endpoint relative to the host
            json=data,
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
        log_metrics()
        random.seed(time.time())
        self.username = random.choice(USERNAMES)
        data = {"username": self.username, "password":self.username}
        start_time = time.time()
        with self.client.post(
            "/login", json=data,
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
        log_metrics()
        random.seed(time.time())
        data = {"numrows": 1}
        start_time = time.time()
        with self.client.post(
            "/register", json=data,
            catch_response=True
        ) as response:
            end_time = time.time()
            if response.status_code == 200:
                response.success()
                print(f"Register Request took {end_time - start_time:.2f} seconds")
            else:
                response.failure(f"Failed with status code {response.status_code}: {response.text}")
