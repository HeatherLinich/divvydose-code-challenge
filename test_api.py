import requests
from requests.models import Response
import json
import os
import pytest

import requests
from requests.models import Response

BASE_URL = 'http://127.0.0.1:5000/v1/'
GOOD_ORG = 'mailchimp'
BAD_ORG = 'testingonlyfordivvydose'

def test_get_bitbucket():
    response = requests.get(BASE_URL + 'bitbucket?org=' + GOOD_ORG)
    assert response.status_code == 200

def test_get_github():
    response = requests.get(BASE_URL + 'github?org=' + GOOD_ORG)
    assert response.status_code == 200

def test_get_combo():
    response = requests.get(BASE_URL + 'comboorgs?org=' + GOOD_ORG)
    assert response.status_code == 200

def test_get_bitbucket_not_exist():
    response = requests.get(BASE_URL + 'bitbucket?org=' + BAD_ORG)
    assert response.status_code == 404

def test_get_github_not_exist():
    response = requests.get(BASE_URL + 'github?org=' + BAD_ORG)
    assert response.status_code == 404

def test_get_bitbucket_not_exist():
    response = requests.get(BASE_URL + 'comboorgs?org=' + BAD_ORG)
    assert response.status_code == 404

def test_get_bitbucket_missing_parameter():
    response = requests.get(BASE_URL + 'bitbucket')
    assert response.status_code == 400

def test_get_github_missing_parameter():
    response = requests.get(BASE_URL + 'github')
    assert response.status_code == 400

def test_get_combo_missing_parameter():
    response = requests.get(BASE_URL + 'comboorgs')
    assert response.status_code == 400
