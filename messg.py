import requests
from requests.auth import HTTPBasicAuth

url = "https://apisms.beem.africa/v1/send"

data = {
    "source_addr": "innobanks",
    "encoding": 0,
    "message": "HELLO MY CUSTOMER, To ensure optimal performance and increase disk space for InnoBanks",
    "recipients": [
        {
            "recipient_id": 1,
            "dest_addr": "255769374866"
        }
    ]
}

username = "fa41fbc274f5097c"
password = "YzVhOTRlYmNhMmRkYWU5ZjBlYzUyY2U1NmNmYTNkNmIzZjZkODc3MjQzNDk3ZWMyNDE3MTJjN2Q5NTVlMTI2NA=="

response = requests.post(url, json=data, auth=HTTPBasicAuth(username, password))

if response.status_code == 200:
    print("SMS sent successfully!")
else:
    print("SMS sending failed. Status code:", response.status_code)
    print("Response:", response.text)