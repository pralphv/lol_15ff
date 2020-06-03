from typing import Dict, Union

import requests

import pandas as pd

try:
    from .. import champion_api
except (ImportError, ValueError):
    from src import champion_api

URL = 'https://acs-garena.leagueoflegends.com/v1/stats/player_history/{region}/{summoner_id}?begIndex=0&endIndex=20'
ATTRIBUTES = ['kills', 'deaths', 'assists', 'win', 'championId']
SOLO_Q_ID = 420
FLEX_Q_ID = 440


def _fetch_summoner_history(region: str, summoner_id: int) -> Dict:
    resp = requests.get(URL.format(region=region, summoner_id=summoner_id))
    return resp.json()


def _filter_last_n_ranked_games(summoner_object: Dict, last_n_games: int, game_id: int) -> pd.DataFrame:
    df = pd.DataFrame(summoner_object['games']['games'])
    df = df[df['queueId'].isin({SOLO_Q_ID, FLEX_Q_ID})]
    df = df[df['gameId'] < game_id]
    df = df[-last_n_games:]
    return df


def _extract_stats(row):
    obj = row['participants'][0]['stats']
    return obj['kills'], obj['deaths'], obj['assists'], obj['win'], row['participants'][0]['championId']


def fetch_summoner_match_history(region: str, summoner_id: int, game_id: Union[int, float]) -> Dict:
    summoner_object = _fetch_summoner_history(region, summoner_id)
    summoner_df = _filter_last_n_ranked_games(summoner_object, 5, game_id)
    summoner_df[ATTRIBUTES] = summoner_df.apply(
        _extract_stats,
        axis=1,
        result_type='expand'
    )
    champion_id_map = champion_api.fetch_champion_id_map()
    summoner_df['champion'] = summoner_df['championId'].replace(champion_id_map)
    summoner_match_history = {
        'summonerName': summoner_df['participantIdentities'].iloc[0][0]['player']['summonerName'],
        'gameHistory': summoner_df[ATTRIBUTES + ['gameCreation', 'champion']].to_dict(orient='records')
    }
    return summoner_match_history


def main():
    summoner_id = 14799593
    region = 'TW'
    game_id = 1803381421
    summoner_object = fetch_summoner_match_history(region, summoner_id, game_id)
    print(summoner_object)


if __name__ == '__main__':
    main()
