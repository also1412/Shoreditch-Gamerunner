from bottle import request, response
from bottle import get, post
from bottle import abort
from uuid import uuid4

from storage import use_db
from util import require_json
from util import sanitise
import util

from config import MAX_PLAYERS

import logic

@post('/player')
@require_json('name', 'endpoint')
@use_db
def add_player(db, json):
	player = util.add_player(db, json['name'], json['endpoint'], json.get('id'))
	
	response.status = 201
	return {"player": player}

@get('/players')
@use_db
def list_players(db):
	players = [sanitise(player) for player in db.get_by_type('player')]
	return {"players": players}

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