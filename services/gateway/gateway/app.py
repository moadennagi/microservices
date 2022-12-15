"API gateway"

import requests

from typing import Union
from flask import Flask, request


app = Flask(__name__)

# FIXME: move to configuration
AUTH_SERVICE = 'auth:5000'
SCRAPPER_SERVICE = 'scrapper:5557'

def authenticate(func):
    "Wraps the route, checks the token"
    
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            res = requests.post(f'http://{AUTH_SERVICE}/validate',
                                headers={'Authorization': auth_header})
            print(res)
            if res.status_code == 200:
                return func(*args, **kwargs)

        return 'unauthorized', 401
    return wrapper


@app.post('/scrap')
@authenticate
def scrap() -> Union[tuple[list[dict], int], tuple[str, int]]:
    """
    """
    auth_header = request.headers['Authorization']
    res = requests.post(f'http://{SCRAPPER_SERVICE}/scrap', headers={'Authorization': auth_header})
    if res.status_code == 200:
        return res.json()
    return 'Not found', 404


@app.post('/login')
def login() -> tuple[str, int]:
    ""
    # Forward request to auth service
    response = requests.post(f'http://{AUTH_SERVICE}/login', headers=request.headers)
    if response.status_code == 200:
        token = response.text
        return token, 200
    return 'unauthorized', 401

@app.get('/')
def home() -> tuple[str, int]:
    ""
    return 'gateway', 200