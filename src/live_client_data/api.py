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


def fetch_game_players() -> Dict:
    active_player = _fetch_active_player()
    url = 'https://127.0.0.1:2999/liveclientdata/playerlist'
    resp = requests.get(url, verify=False)
    objects = resp.json()
    chaos_team = filter(lambda obj: obj['team'] == 'CHAOS', objects)
    order_team = filter(lambda obj: obj['team'] == 'ORDER', objects)
    chaos_summoner_names = list(map(lambda obj: obj['summonerName'], chaos_team))
    order_summoner_names = list(map(lambda obj: obj['summonerName'], order_team))

    chaos_summoner_ids = list(map(
        lambda summoner_name: league_client_api.find_account_id_by_account_name(summoner_name),
        chaos_summoner_names
    ))

    order_summoner_ids = list(map(
        lambda summoner_name: league_client_api.find_account_id_by_account_name(summoner_name),
        order_summoner_names
    ))

    return {
        'myTeam': chaos_summoner_ids if active_player in chaos_summoner_ids else order_summoner_ids,
        'enemyTeam': order_summoner_ids if active_player in order_summoner_ids else chaos_summoner_ids,
    }


def fetch_game_players_match_history() -> Dict:
    players_obj = fetch_game_players()
    my_team_match_history = map(
        lambda account_id: summoner_api.fetch_summoner_match_history('TW', account_id, float('inf')),
        players_obj['myTeam']
    )
    enemy_team_match_history = map(
        lambda account_id: summoner_api.fetch_summoner_match_history('TW', account_id, float('inf')),
        players_obj['enemyTeam']
    )
    return {'myTeam': list(my_team_match_history), 'enemyTeam': list(enemy_team_match_history)}


def main():
    print(fetch_game_players())


if __name__ == '__main__':
    main()
