import csv
from pymongo import MongoClient

# Connect to MongoDB
uri = "mongodb+srv://lokranjan03:loki2003@cluster0.klgxr.mongodb.net/authdata?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client["authdata"]
users_collection = db["users"]

# Fetch all users
users = users_collection.find({}, {"_id": 0, "username": 1})  # Retrieve only the 'username' field

# Write to CSV
output_file = "usernames.csv"
with open(output_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Username"])  # Write header

    for user in users:
        writer.writerow([user["username"]])

print(f"Usernames successfully exported to {output_file}")
