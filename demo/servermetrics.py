import psutil
import os
import csv
import time

# File to store the metrics
csv_file = "server_metrics.csv"

# Write headers to CSV
with open(csv_file, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["timestamp", "cpu_percent", "memory_percent", "disk_io",
                     "net_io_sent", "net_io_recv", "load_avg", "active_connections"])

# Function to log metrics
def log_metrics():
    # Timestamp
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    # System Metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_percent = psutil.virtual_memory().percent
    disk_io = psutil.disk_io_counters().write_bytes
    net_io = psutil.net_io_counters()
    net_io_sent = net_io.bytes_sent
    net_io_recv = net_io.bytes_recv
    load_avg = os.getloadavg()[0]
    # Active Connections
    active_connections = len(psutil.net_connections(kind='inet'))


if __name__ == "__main__":
    log_metrics()
