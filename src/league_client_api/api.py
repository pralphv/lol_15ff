from typing import List, Dict
import requests

try:
    import lockfile
    from .. import summoner_api
    from .. import live_client_data
except ImportError:
    from src.league_client_api import lockfile
    from src import summoner_api
    from src import live_client_data

USER_DETAILS = 'https://127.0.0.1:{{port}}/lol-summoner/v1/summoners/{summoner_id}'
MY_TEAM_SUMMONERS = 'https://127.0.0.1:{port}/lol-champ-select/v1/session'
RANK_STATS = 'https://127.0.0.1:{{port}}/lol-ranked/v1/ranked-stats/{puuid}'
ACCEPT_MATCH = 'https://127.0.0.1:{port}/lol-matchmaking/v1/ready-check/accept'
PLAYERS = 'https://127.0.0.1:{port}/lol-gameflow/v1/session'
GAME_STATUS = 'https://127.0.0.1:{port}/lol-gameflow/v1/gameflow-phase'


def request_to_league_client(url: str, method: str = 'GET'):
    request_method = requests.post if method == 'POST' else requests.get
    lockfile_dict = lockfile.get_lockfile_content()
    encrypted_auth = lockfile_dict['encrypted']
    url = url.format(port=lockfile_dict['port'])
    try:
        resp = request_method(
            url,
            headers={"Content-Type": "application/json", 'Authorization': f'Basic {encrypted_auth}'},
            verify=False
        )
        return resp
    except Exception as e:
        lockfile.clear_cache()
        raise RuntimeError('Error when querying client. League may have been closed.')


def find_account_id_by_account_name(account_name: str) -> str:
    url = f'https://acs-garena.leagueoflegends.com/v1/players?name={account_name}&region=TW'
    resp = requests.get(url)
    return resp.json()['accountId']


def find_account_ids_by_summoner_id(summoner_id: int) -> Dict:
    resp = request_to_league_client(USER_DETAILS.format(summoner_id=summoner_id))
    return resp.json()


def fetch_my_teams_match_history() -> List[Dict]:
    resp = request_to_league_client(MY_TEAM_SUMMONERS)
    content = resp.json()
    print(content)
    try:
        summoners = list(map(
            lambda obj: {
                'summoner_id': obj['summonerId'],
                'championId': obj['championId'],
            }
            ,
            content['myTeam'])
        )
        account_ids = map(
            lambda summoner_obj: {
                **find_account_ids_by_summoner_id(summoner_obj['summoner_id']),
                **summoner_obj
            },
            summoners
        )
        summoner_match_history = map(
            lambda account_obj: {
                **summoner_api.fetch_summoner_match_history('TW', account_obj['accountId'], float('inf')),
                'ranked_stats': fetch_ranked_stats(account_obj['summonerId'])
            },
            account_ids
        )
        return list(summoner_match_history)
    except KeyError as e:
        return None


def fetch_ranked_stats(summoner_id: int = None, puuid: str = None):
    if not summoner_id and not puuid:
        return None
        # raise RuntimeError('Must provide either summoner_id or puuid')
    if not puuid:
        puuid = find_account_ids_by_summoner_id(summoner_id)['puuid']
    resp = request_to_league_client(RANK_STATS.format(puuid=puuid))
    content = resp.json()
    stats = {
        'flex': content['queueMap']['RANKED_FLEX_SR'],
        'solo': content['queueMap']['RANKED_SOLO_5x5'],
    }
    return stats


def fetch_game_players() -> Dict:
    resp = request_to_league_client(PLAYERS)
    team_1 = resp.json()['gameData']['teamOne']
    team_2 = resp.json()['gameData']['teamTwo']
    summoner_to_champion_map = live_client_data.fetch_summoner_champion_map()
    team_1 = map(
        lambda obj: {
            'summonerName': obj['summonerName'],
            'champion': summoner_to_champion_map[obj['summonerName']],
            **summoner_api.fetch_summoner_match_history('TW', int(obj['accountId']), float('inf')),
            'ranked_stats': fetch_ranked_stats(puuid=obj['puuid'])
        },
        team_1
    )

    team_2 = map(
        lambda obj: {
            'summonerName': obj['summonerName'],
            'champion': summoner_to_champion_map[obj['summonerName']],
            **summoner_api.fetch_summoner_match_history('TW', int(obj['accountId']), float('inf')),
            'ranked_stats': fetch_ranked_stats(puuid=obj['puuid'])
        },
        team_2
    )
    return {'team1': list(team_1), 'team2': list(team_2)}


def fetch_game_status() -> str:
    try:
        resp = request_to_league_client(GAME_STATUS)
        return resp.text[1:-1]  # "InProgress", not InProgress
    except Exception as e:
        print(e)
        return 'not running'


def accept_match():
    resp = request_to_league_client(ACCEPT_MATCH, 'POST')
    if resp.text == '':
        return 'success'
    else:
        return resp.json()


def main():
    print(fetch_my_teams_match_history())
    return
    import time
    while True:
        try:
            resp = fetch_my_teams_match_history()
            print(resp)
        except Exception as e:
            print("ERROR", e)
        time.sleep(2)


if __name__ == '__main__':
    main()
