import requests

url = "http://127.0.0.1:7019/otp"
data = {"username": "lokranjan"}
response = requests.post(url, json=data)
print(response.json())
