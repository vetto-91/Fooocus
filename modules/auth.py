import hmac
import json
import hashlib
import modules.constants as constants

from os.path import exists

_DUMMY_HASH = '0' * 64


def auth_list_to_dict(auth_list):
    auth_dict = {}
    for auth_data in auth_list:
        if 'user' in auth_data:
            if 'hash' in auth_data:
                auth_dict |= {auth_data['user']: str(auth_data['hash'])}
            elif 'pass' in auth_data:
                print(f"[Security Warning] Plaintext password detected in {constants.AUTH_FILENAME} for user '{auth_data['user']}'. Consider using a hashed entry or placing Fooocus behind a reverse proxy with strong authentication.")
                auth_dict |= {auth_data['user']: hashlib.sha256(bytes(auth_data['pass'], encoding='utf-8')).hexdigest()}
    return auth_dict


def load_auth_data(filename=None):
    auth_dict = None
    if filename is not None and exists(filename):
        with open(filename, encoding='utf-8') as auth_file:
            try:
                auth_obj = json.load(auth_file)
                if isinstance(auth_obj, list) and len(auth_obj) > 0:
                    auth_dict = auth_list_to_dict(auth_obj)
            except Exception as e:
                print('load_auth_data, e: ' + str(e))
    return auth_dict


auth_dict = load_auth_data(constants.AUTH_FILENAME)

auth_enabled = auth_dict is not None


def check_auth(user, password):
    if not auth_dict or not isinstance(user, str) or not isinstance(password, str):
        return False
    expected_hash = auth_dict.get(user)
    provided_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    if expected_hash is None:
        hmac.compare_digest(provided_hash, _DUMMY_HASH)
        return False
    return hmac.compare_digest(provided_hash, expected_hash)
