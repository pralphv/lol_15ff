from functools import lru_cache
import requests


def _fetch_league_latest_version():
    url = 'https://ddragon.leagueoflegends.com/api/versions.json'
    resp = requests.get(url)
    data = resp.json()
    return data[0]


@lru_cache
def fetch_champion_id_map():
    latest_league_version = _fetch_league_latest_version()
    url = f'http://ddragon.leagueoflegends.com/cdn/{latest_league_version}/data/en_US/champion.json'
    resp = requests.get(url)
    data = resp.json()
    champion_id_map = {}
    for key, champion_obj in data['data'].items():
        champion_id_map[int(champion_obj['key'])] = key
    return champion_id_map


def main():
    print(fetch_champion_id_map())

if __name__ == '__main__':
    main()