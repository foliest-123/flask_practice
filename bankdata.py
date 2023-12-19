import requests

data = [{
    "net_amount": 3000,
    "mode": "withdraw",
    "amount": 10
}]

# URL of the Flask endpoint
url = 'http://127.0.0.1:5000/bankdata'

# Sending a POST request with JSON data to the Flask endpoint
response = requests.post(url, json=data)

# Checking the response
if response.status_code == 200:
    print("Success!..", response.json())
else:
    print("Error:", response.json())





