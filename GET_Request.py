import requests

url = 'http://185.18.54.154:8000/myapp/receive_data/'
url2 = 'http://185.18.54.154:8000/myapp/clear_data/'

def clear_table():
    global url2
    response = requests.get(url2)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)

response = requests.get(url)

if response.status_code == 200:
    table = response.json().get('table', [])
    print("Received Table:")
    for entry in table:
        print(entry)
else:
    print(f"Error: {response.status_code}")
    print(response.text)