# import requests

# url = "https://www.wasenderapi.com/api/send-message"

# headers = {
#     "Authorization": "Bearer e962b7bb3462376daf4bf55aa2d870a1500d76a61b2ae1b9de4d208484f46233",
#     "Content-Type": "application/json"
# }

# data = {
#     "to": "255770036452",
#     "text": "Hello from my WhatsApp API "
# }

# response = requests.post(url, json=data, headers=headers)

# print(response.status_code)
# print(response.text)



#Check Session
# import requests

# url = "https://www.wasenderapi.com/api/whatsapp-sessions"
# headers = {
#     "Authorization": "Bearer 4165|OxiUBxNppTw3jN7KtHPdg8qQZ8nGGnbJOLuOjFPYc2bfccf9"
# }
# response = requests.get(url, headers=headers)
# print(response.json())


import requests


import requests

url = "https://www.wasenderapi.com/api/messages/{msgId}"
headers = {
    "Authorization": "Bearer 183fbc9afb7eb4a8277776b174a84ca9977fd6a67e284bf06b15916516ea62a5"
}
response = requests.delete(url, headers=headers)
print(response.json())