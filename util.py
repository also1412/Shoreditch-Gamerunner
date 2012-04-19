from uuid import uuid4
from copy import copy

from bottle import request
from bottle import abort



def require_json(*fields):
	def require_json_inner(f):
		def inner_func(*args, **kwargs):
			if not 'json' in kwargs:
				if not request.json:
					abort(400, 'Must use Content-type of application/json')
				kwargs['json'] = request.json

			for field in fields:
				if not field in kwargs['json']:
					abort(400, 'Must pass "%s"' % field)
			return f(*args, **kwargs)
		return inner_func
	return require_json_inner

def use_game(f):
	def inner_func(db, game_id, *args, **kwargs):
		game = db.get(game_id)
		if not game:
			abort(400, "Invalid game id")
		return f(db, game, *args, **kwargs)
	return inner_func

def require_player(f):
	def inner_func(db, game, *args, **kwargs):
		if not 'json' in kwargs:
			if not request.json:
				abort(400, 'Must use Content-type of application/json')
			kwargs['json'] = request.json

		if not 'player_id' in kwargs['json']:
			abort(400, "Must pass player_id")

		player_id = kwargs['json']['player_id']

		if not player_id in game['players']:
			abort(400, "Player not part of game")

		player = game['players'][player_id]
		del kwargs['json']
		return f(db, game, player, *args, **kwargs)
	return inner_func


# Remove sensitive data from a document
def sanitise(doc):
	doc = copy(doc)
	del doc['secret']
	return doc

def add_player(db, name, endpoint, player_id=None):
	if not player_id:
		player_id = uuid4().hex
	player_secret = uuid4().hex

	player = {
		"id": player_id,
		"type": "player",
		"secret": player_secret,
		"name": name,
		"endpoint": endpoint
	}

	db.save(player)
	return player