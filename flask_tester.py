import requests

def test_logs_endpoint():
    try:
        response = requests.get("http://127.0.0.1:7019/logs")

        if response.status_code != 200:
            print(f"Test Failed: HTTP Status Code {response.status_code}")
            return

        data = response.json()
        print(data)

        expected_keys = [
            "timestamp",
            "cpu_percent",
            "memory_percent",
            "disk_io",
            "net_io_sent",
            "net_io_recv",
            "load_avg",
            "active_connections"
        ]

        for key in expected_keys:
            if key not in data:
                print(f"Test Failed: Missing key '{key}' in response")
                return

        if not isinstance(data["timestamp"], str):
            print("Test Failed: 'timestamp' should be a string")
            return

        if not (0 <= data["cpu_percent"] <= 100):
            print("Test Failed: 'cpu_percent' should be between 0 and 100")
            return

        if not (0 <= data["memory_percent"] <= 100):
            print("Test Failed: 'memory_percent' should be between 0 and 100")
            return

        if not isinstance(data["disk_io"], (int, float)):
            print("Test Failed: 'disk_io' should be a number")
            return

        if not isinstance(data["net_io_sent"], (int, float)):
            print("Test Failed: 'net_io_sent' should be a number")
            return

        if not isinstance(data["net_io_recv"], (int, float)):
            print("Test Failed: 'net_io_recv' should be a number")
            return

        if data["load_avg"] is not None and not isinstance(data["load_avg"], (int, float)):
            print("Test Failed: 'load_avg' should be a number or None")
            return

        if not isinstance(data["active_connections"], (int, str)):
            print("Test Failed: 'active_connections' should be a number or 'Permission Denied'")
            return

        print("Test Passed: All checks passed successfully")

    except Exception as e:
        print(f"Test Failed: Exception occurred - {e}")

if __name__ == "__main__":
    test_logs_endpoint()
