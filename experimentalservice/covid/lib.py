import requests
import json

def get_user_id(email, name):
    url = "http://localhost:3000/api/user"
    data = {
        'email': 'mrander@umich.edu',
        'name': 'Mike Anderson'
    }
    headers = {'Content-type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(data))

    user_data = response.json()
    user_id = user_data['id']

    return user_id
