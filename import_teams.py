import csv
import requests

CTFD_URL = "http://172.23.80.1:8000"  # Change to your CTFd URL (ensure this matches your running server)
ADMIN_TOKEN = "ctfd_3c985ed77c1ae993ce3b3bcb2c6f48d236faa52af73411eddbd8828eddfcb3f3"  # Replace with your admin token
CSV_FILE = "importdata/teams.csv"  # Use forward slashes for cross-platform compatibility

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Token {ADMIN_TOKEN}"
}

def create_user(name, password, affiliation=""):
    data = {
        "name": name,
        "password": password,
        "affiliation": affiliation
    }
    url = f"{CTFD_URL}/api/v1/users"
    try:
        resp = requests.post(url, json=data, headers=HEADERS)
    except Exception as e:
        print(f"✗ Exception for user {name}: {e}")
        return
    if resp.status_code == 200:
        print(f"✓ Created user: {name}")
    else:
        print(f"✗ Failed to create user {name}: {resp.status_code} {resp.text}")
        if resp.status_code == 404:
            print(f"  → 404 Not Found: Check if the API endpoint {url} is correct and the server is running.")
        elif resp.status_code == 401:
            print(f"  → 401 Unauthorized: Check if your ADMIN_TOKEN is correct and has admin privileges.")

with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    required_headers = {"name", "password"}
    if not required_headers.issubset(reader.fieldnames):
        print(f"CSV file must contain headers: {', '.join(required_headers)}")
    else:
        for row in reader:
            create_user(row["name"], row["password"], row.get("affiliation", ""))