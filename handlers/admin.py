from bottle import request, response
from bottle import post
from uuid import uuid4

from storage import use_db
from util import require_json

@post('/player')
@require_json('name', 'endpoint')
@use_db
def register(db):
	player_id = request.json.get('id', uuid4().hex)
	player_secret = uuid4().hex

	player = {
		"id": player_id,
		"type": "player",
		"secret": player_secret,
		"name": request.json['name'],
		"endpoint": request.json['endpoint']
	}

	db.save(player)

	response.status = 201
	return {"player": player}