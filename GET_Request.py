import requests

url = 'http://185.18.54.154:8000/myapp/receive_data/'
response = requests.get(url)

if response.status_code == 200:
    table = response.json().get('table', [])
    print("Received Table:")
    for entry in table:
        print(entry)
else:
    print(f"Error: {response.status_code}")
    print(response.text)