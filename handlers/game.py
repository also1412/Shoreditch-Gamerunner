from bottle import get, post
from bottle import abort

from util import require_json
from storage import use_db

from config import MIN_PLAYERS, MAX_PLAYERS

import logic

@post('/game')
@require_json('players')
@use_db
def start_game(db, json):
	players = db.get_by_keys(json['players'])
	if len(players) < len(json['players']):
		abort(400, "Not all players exist")

	if len(players) > MAX_PLAYERS:
		abort(400, "Can not have more than %i players in one game" % MAX_PLAYERS)

	if len(players) < MIN_PLAYERS:
		abort(400, "Can not have less than %i players in a game" % MIN_PLAYERS)

	game_id = logic.start_game(db, players)

	return {"game_id": game_id}