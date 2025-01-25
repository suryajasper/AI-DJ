import json
import os

def get_secrets_json():
    filename = os.path.join('secrets.json')
    try:
        with open(filename, mode='r') as f:
            return json.loads(f.read())
    except FileNotFoundError:
        print('secrets.json not found')
        return {}

def retrieve_key(api : str) -> str:
    try:
        return get_secrets_json()["keys"][api]
    except:
        return ''