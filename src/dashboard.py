import requests
import socket
import urllib3
import webbrowser

from flask import Flask, render_template, jsonify, make_response, request

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

try:
    from .summoner_api import fetch_summoner_match_history
    from .league_client_api import fetch_my_teams_match_history, fetch_game_players, fetch_game_status, accept_match
    from .live_client_data import fetch_game_players_match_history
    from .game_api import fetch_game_stats, fetch_game_time
except ImportError:
    from summoner_api import fetch_summoner_match_history
    from league_client_api import fetch_my_teams_match_history, fetch_game_players, fetch_game_status, accept_match
    from live_client_data import fetch_game_players_match_history
    from game_api import fetch_game_stats, fetch_game_time

PREDICTION_URL = 'https://lol-15ff-model.herokuapp.com/'


@app.route("/")
def landing_page():
    return render_template('index.html')


@app.route("/accept-game")
def accept_matchmaking():
    resp = accept_match()
    if resp != 'success':
        msg = resp['message']
    else:
        msg = 'success'
    resp = jsonify({
        'msg': msg,
    })
    return resp


@app.route("/game-state")
def get_game_state():
    status = fetch_game_status()
    if status == 'None':
        msg = 'Not in game'
    elif status == 'ChampSelect':
        msg = 'In champion select'
    elif status == 'InProgress':
        msg = 'In Game'
    elif status == 'not running':
        msg = 'League not running'
    else:
        msg = status

    resp = jsonify({
        'msg': msg,
    })

    return resp


@app.route("/champion-select-bundle")
def fetch_team_history():
    summoner_ids = fetch_my_teams_match_history()  # this function goes through every process so it could act as a check
    resp = jsonify({
        'msg': 'In champion select',
        'payload': summoner_ids
    })
    return make_response(resp, 200)


@app.route("/ingame-bundle")
def fetch_ingame_history():
    players_obj = fetch_game_players()
    resp = jsonify({
        'msg': 'In Game',
        'payload': players_obj
    })
    return make_response(resp, 404)


@app.route("/predict")
def predict_15():
    game_stats = fetch_game_stats()
    model = request.args.get('model', type=int)
    resp = requests.post(PREDICTION_URL + f'api/{model}', json=game_stats)
    resp = resp.json()
    if resp['status'] == 'ok':
        msg = 'success'
        payload = resp['msg']['winningTeam']
    else:
        msg = 'failed'
        payload = None

    data = jsonify({
        'msg': msg,
        'payload': payload
    })
    return make_response(data, 200)


@app.route("/check-game-time")
def check_game_time():
    time = fetch_game_time()
    data = jsonify({
        'msg': 'success',
        'payload': time
    })
    return make_response(data, 200)


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 0))
    port = sock.getsockname()[1]
    sock.close()
    webbrowser.open_new(f'http://127.0.0.1:{port}/')
    app.run(debug=False, port=port)
