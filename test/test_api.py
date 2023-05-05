import pytest
import requests
from database.models import User

# from time import sleep

API_BASE = "http://127.0.0.1:5000"


def test_user_creation():
    register_post_data = {
        "username": "test",
        "password": "test",
        "phone": "+37011111111",
    }
    response = requests.post(f"{API_BASE}/register", json=register_post_data)
    print(response.content)
    assert response.status_code == 200


def test_user_creation_duplicate():
    register_post_data = {
        "username": "test",
        "password": "test",
        "phone": "+37011111111",
    }
    response = requests.post(f"{API_BASE}/register", json=register_post_data)
    print(response.content)
    assert response.status_code == 400


def test_user_update_username():
    login_post_data = {"username": "test", "password": "test"}
    response = requests.post(f"{API_BASE}/login", json=login_post_data)

    # logged in
    user_json = response.json()
    user_json["username"] = "new_username"
    response = requests.put(f"{API_BASE}/update/username", json=user_json)
    assert response.status_code == 200
    # update assert
    new_login_post_data = {"username": "new_username", "password": "test"}
    response = requests.post(f"{API_BASE}/login", json=new_login_post_data)
    assert response.status_code == 200
    # login with new username assert
    login_post_data = {"username": "test", "password": "test"}
    response = requests.post(f"{API_BASE}/login", json=login_post_data)
    assert response.status_code == 401
    # login with old username fails


def test_user_update_password():
    register_post_data = {
        "username": "test",
        "password": "test",
        "phone": "+37022222222",
    }
    response = requests.post(f"{API_BASE}/register", json=register_post_data)
    assert response.status_code == 200

    login_post_data = {"username": "test", "password": "test"}
    response = requests.post(f"{API_BASE}/login", json=login_post_data)

    # logged in
    user_json = response.json()
    user_json["password"] = "new_password"
    response = requests.put(f"{API_BASE}/update/password", json=user_json)
    assert response.status_code == 200
    # update assert
    new_login_post_data = {"username": "test", "password": "new_password"}
    response = requests.post(f"{API_BASE}/login", json=new_login_post_data)
    assert response.status_code == 200
    # login with new password assert
    login_post_data = {"username": "test", "password": "test"}
    response = requests.post(f"{API_BASE}/login", json=login_post_data)
    assert response.status_code == 401
    # login with old password fails


def test_user_update_phone():
    register_post_data = {
        "username": "test2",
        "password": "test2",
        "phone": "+37033333333",
    }
    response = requests.post(f"{API_BASE}/register", json=register_post_data)
    recovery_code = response.json()["rec1"]
    assert response.status_code == 200

    login_post_data = {"username": "test2", "password": "test2"}
    response = requests.post(f"{API_BASE}/login", json=login_post_data)
    user_json = response.json()
    user_json["backup_code"] = recovery_code
    user_json["new_phone"] = "+37044444444"
    response = requests.put(f"{API_BASE}/update/phone", json=user_json)
    phone_json = {"phone": "+37044444444"}
    response = requests.post(f"{API_BASE}/get_phone", json=phone_json)
    assert response.status_code == 200
    # user with phone exists

    phone_json = {"phone": "+37033333333"}
    response = requests.post(f"{API_BASE}/get_phone", json=phone_json)
    assert response.status_code == 400
    # user with old phone no longer exists


def test_user_delete():
    register_post_data = {
        "username": "test3",
        "password": "test3",
        "phone": "+37055555555",
    }
    response = requests.post(f"{API_BASE}/register", json=register_post_data)
    assert response.status_code == 200

    login_post_data = {"username": "test3", "password": "test3"}
    response = requests.post(f"{API_BASE}/login", json=login_post_data)
    user_json = response.json()
    
    response = requests.delete(f"{API_BASE}/delete", json=user_json)
    assert response.status_code == 200
    # deletion successful

    login_post_data = {"username": "test3", "password": "test3"}
    response = requests.post(f"{API_BASE}/login", json=login_post_data)
    assert response.status_code == 401
    # no longer able to log in with deleted details