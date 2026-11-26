import hmac
import json
import hashlib
import threading
import time
import modules.constants as constants

from os.path import exists

_DUMMY_HASH = '0' * 64
_AUTH_LOCK = threading.Lock()
_FAILED_ATTEMPTS: dict[str, list[float]] = {}
_MAX_FAILED_ATTEMPTS = 10
_RATE_WINDOW_SECONDS = 60.0


def _verify_password(password: str, stored: str) -> bool:
    """Verify password against pbkdf2_sha256$<iters>$<salt_hex>$<hash_hex> or legacy SHA-256 hex."""
    if stored.startswith('pbkdf2_sha256$'):
        try:
            _, iter_str, salt_hex, hash_hex = stored.split('$', 3)
            iterations = int(iter_str)
            dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt_hex), iterations)
            return hmac.compare_digest(dk.hex(), hash_hex)
        except Exception:
            return False
    provided_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return hmac.compare_digest(provided_hash, stored)


def auth_list_to_dict(auth_list):
    auth_dict = {}
    for auth_data in auth_list:
        if 'user' in auth_data:
            if 'hash' in auth_data:
                auth_dict |= {auth_data['user']: str(auth_data['hash'])}
            elif 'pass' in auth_data:
                print(f"[Security Warning] Plaintext password detected in {constants.AUTH_FILENAME} for user '{auth_data['user']}'. Consider using a pbkdf2_sha256 hashed entry or placing Fooocus behind a reverse proxy with strong authentication.")
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

    now = time.monotonic()
    with _AUTH_LOCK:
        attempts = [t for t in _FAILED_ATTEMPTS.get(user, []) if now - t < _RATE_WINDOW_SECONDS]
        if len(attempts) >= _MAX_FAILED_ATTEMPTS:
            _FAILED_ATTEMPTS[user] = attempts
            return False

    expected_hash = auth_dict.get(user)
    if expected_hash is None:
        hmac.compare_digest(hashlib.sha256(password.encode('utf-8')).hexdigest(), _DUMMY_HASH)
        ok = False
    else:
        ok = _verify_password(password, expected_hash)

    with _AUTH_LOCK:
        if ok:
            _FAILED_ATTEMPTS.pop(user, None)
        else:
            attempts = [t for t in _FAILED_ATTEMPTS.get(user, []) if now - t < _RATE_WINDOW_SECONDS]
            attempts.append(now)
            _FAILED_ATTEMPTS[user] = attempts

    return ok
