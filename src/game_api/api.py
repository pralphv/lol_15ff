from typing import Dict

import requests

GAME_URL = 'https://acs-garena.leagueoflegends.com/v1/stats/game/{region}/{game_id}'


def _fetch_ingame_data():
    url = 'https://127.0.0.1:2999/liveclientdata/allgamedata'
    resp = requests.get(url, verify=False)
    return resp.json()


def fetch_game_time():
    url = 'https://127.0.0.1:2999/liveclientdata/gamestats'
    resp = requests.get(url, verify=False)
    return resp.json()['gameTime']


def extract_events(data):
    events = data['events']['Events']
    order_team = list(filter(lambda obj: obj['team'] == 'ORDER', data['allPlayers']))
    chaos_team = list(filter(lambda obj: obj['team'] == 'CHAOS', data['allPlayers']))

    order_players = list(map(lambda obj: obj['summonerName'], order_team))
    chaos_players = list(map(lambda obj: obj['summonerName'], chaos_team))

    baron_kills = list(filter(lambda obj: obj['EventName'] == 'BaronKill', events))
    dragon_kills = list(filter(lambda obj: obj['EventName'] == 'DragonKill', events))
    herald_kills = list(filter(lambda obj: obj['EventName'] == 'HeraldKill', events))
    turret_kills = list(filter(lambda obj: obj['EventName'] == 'TurretKilled', events))
    inhib_kills = list(filter(lambda obj: obj['EventName'] == 'InhibKilled', events))

    team_2_turrets = sum(1 if 'T1' in turret_kill['TurretKilled'] else 0 for turret_kill in turret_kills)
    team_1_turrets = sum(1 if 'T2' in turret_kill['TurretKilled'] else 0 for turret_kill in turret_kills)

    team_2_inhibs = sum(1 if 'T1' in turret_kill['InhibKilled'] else 0 for turret_kill in inhib_kills)
    team_1_inhibs = sum(1 if 'T2' in turret_kill['InhibKilled'] else 0 for turret_kill in inhib_kills)

    team_1_herald = sum(1 if herald_kill['KillerName'] in order_players else 0 for herald_kill in herald_kills)
    team_2_herald = sum(1 if herald_kill['KillerName'] in chaos_players else 0 for herald_kill in herald_kills)

    team_1_baron = sum(1 if baron_kill['KillerName'] in order_players else 0 for baron_kill in baron_kills)
    team_2_baron = sum(1 if baron_kill['KillerName'] in chaos_players else 0 for baron_kill in baron_kills)

    team_1_dragon = sum(1 if dragon_kill['KillerName'] in order_players else 0 for dragon_kill in dragon_kills)
    team_2_dragon = sum(1 if dragon_kill['KillerName'] in chaos_players else 0 for dragon_kill in dragon_kills)

    return {
        'order': {
            'turrets': team_1_turrets,
            'herald': team_1_herald,
            'baron': team_1_baron,
            'dragon': team_1_dragon,
            'inhibitors': team_1_inhibs
        },
        'chaos': {
            'turrets': team_2_turrets,
            'herald': team_2_herald,
            'baron': team_2_baron,
            'dragon': team_2_dragon,
            'inhibitors': team_2_inhibs
        }}


def _fetch_game_data(region: str, game_id: int) -> Dict:
    resp = requests.get(
        GAME_URL.format(region=region, game_id=game_id)
    )
    return resp.json()


def _collect_attributes(game_dict: Dict) -> Dict:
    if game_dict['teams'][0]['win'] == 'Win':
        winning_team_id = game_dict['teams'][0]['teamId']
    else:
        winning_team_id = game_dict['teams'][1]['teamId']

    if winning_team_id == 100:
        winning_team = list(map(lambda object: object['player']['accountId'], game_dict['participantIdentities'][:5]))
        losing_team = list(map(lambda object: object['player']['accountId'], game_dict['participantIdentities'][5:]))
    else:
        winning_team = list(map(lambda object: object['player']['accountId'], game_dict['participantIdentities'][5:]))
        losing_team = list(map(lambda object: object['player']['accountId'], game_dict['participantIdentities'][:5]))

    return {
        'gameCreation': game_dict['gameCreation'],
        'winningTeam': winning_team,
        'losingTeam': losing_team,
        'gameMode': game_dict['gameMode'],
        'gameType': game_dict['gameType'],
        'gameId': game_dict['gameId']
    }


def _extract_team_scores(team_object):
    level_sum = sum(obj['level'] for obj in team_object)
    kills_sum = sum(obj['scores']['kills'] for obj in team_object)
    deaths_sum = sum(obj['scores']['deaths'] for obj in team_object)
    assists_sum = sum(obj['scores']['assists'] for obj in team_object)
    cs_sum = sum(obj['scores']['creepScore'] for obj in team_object)
    return {'level': level_sum, 'kills': kills_sum, 'deaths': deaths_sum, 'assists': assists_sum, 'cs': cs_sum}


def fetch_game_stats():
    game_data = _fetch_ingame_data()
    objective_scores = extract_events(game_data)
    order_team = list(filter(lambda obj: obj['team'] == 'ORDER', game_data['allPlayers']))
    chaos_team = list(filter(lambda obj: obj['team'] == 'CHAOS', game_data['allPlayers']))
    order_team_scores = _extract_team_scores(order_team)
    chaos_team_scores = _extract_team_scores(chaos_team)

    game_data = {
        '100': {
            **order_team_scores,
            **objective_scores['order']
        },
        '200': {
            **chaos_team_scores,
            **objective_scores['chaos']
        }
    }
    return game_data


def main():
    # order team is bottom team, aka team 1
    print(fetch_game_time())


if __name__ == '__main__':
    main()
