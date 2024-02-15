
import requests

import requests

url = "https://sandbox.interswitchng.com/virtual-card/api/v1/cards/create/debit"

payload = {
    "accountType": "20",
    "accountId": "1234567890",
    "pin": 1234,
    "firstName": "John",
    "lastName": "Doe",
    "nameOnCard": "John Doe",
    "mobileNr": "23487564738",
    "emailAddress": "johndoe@gmail.com",
    "streetAddress": "24, Royal Valley, Sango",
    "city": "Ilorin",
    "state": "Kwara",
    "countryCode": "NGN"
}
headers = {
    "accept": "application/json",
    "content-type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.text)