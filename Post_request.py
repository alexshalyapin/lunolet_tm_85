import requests
import json

# URL of the Django server
url = 'http://185.18.54.154:8000/myapp/receive_data/'

# Data to send
data = {
    'text': 'Alex',
    'value1': 1,
    'value2': 0,
    'value3': 0,
    'value4': 0
}

# Convert data to JSON
json_data = json.dumps(data)

# Send POST request
headers = {'Content-Type': 'application/json'}
response = requests.post(url, data=json_data, headers=headers)

# Check response
if response.status_code == 200:
    table = response.json().get('table', [])
    print("Received Table:")
    for entry in table:
        print(entry)
else:
    print(f"Error: {response.status_code}")
    print(response.text)