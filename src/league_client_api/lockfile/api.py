from functools import lru_cache
from typing import Dict
import base64

try:
    from ..league_process import find_path_of_league
except ValueError:
    from src.league_client_api.league_process import find_path_of_league


def _read_lockfile() -> Dict:
    path = find_path_of_league()
    with open(path, 'r') as f:
        lock_file = f.read().split(':')
    return {'port': lock_file[2], 'password': lock_file[3]}


@lru_cache
def get_lockfile_content() -> Dict:
    lock_file = _read_lockfile()
    username = 'riot'
    port = lock_file['port']
    password = lock_file['password']
    encrypted_auth = base64.b64encode(f'{username}:{password}'.encode('utf-8')).decode('utf-8')
    print({'username': username, 'port': port, 'password': password, 'encrypted': encrypted_auth})
    return {'username': username, 'port': port, 'password': password, 'encrypted': encrypted_auth}


def clear_cache():
    get_lockfile_content.cache_clear()
