from functools import lru_cache
from typing import Union

import psutil


@lru_cache
def find_path_of_league() -> Union[str, None]:
    league_name = 'LeagueClient.exe'
    for process_id in psutil.pids():
        process = psutil.Process(process_id)
        try:
            if process.name() == league_name:
                return f'{process.exe()[:-len(league_name) - 1]}//lockfile'
        except:  # there can be many reasons why this could not be loaded
            pass
    raise RuntimeError('League is not running')
