from typing import Dict
import requests

try:
    from .. import league_client_api
    from .. import summoner_api
except (ImportError, ValueError):
    from src import league_client_api
    from src import summoner_api


def _fetch_active_player() -> str:
    url = 'https://127.0.0.1:2999/liveclientdata/allgamedata'
    resp = requests.get(url, verify=False)
    return resp.json()['activePlayer']['summonerName']


def fetch_summoner_champion_map() -> Dict:
    url = 'https://127.0.0.1:2999/liveclientdata/playerlist'
    resp = requests.get(url, verify=False)
    list_of_objects = resp.json()
    name_to_champion_map = {obj['summonerName']: obj['championName'] for obj in list_of_objects}
    return name_to_champion_map


def main():
    print(fetch_summoner_champion_map())


if __name__ == '__main__':
    main()
