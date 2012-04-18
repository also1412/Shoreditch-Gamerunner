from bottle import request, response
from bottle import get, post
from bottle import abort
from uuid import uuid4

from storage import use_db
from util import require_json
from util import sanitise
import util

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