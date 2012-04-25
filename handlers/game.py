from uuid import uuid4

from bottle import get, post
from bottle import abort, request

from util import require_json, use_game, require_player
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

	if not 'name' in json:
		json['name'] = uuid4().hex

	game_id = logic.start_game(db, json['name'], players)

	return {"game_id": game_id}

@post('/game/:game_id/end_turn')
@use_db
@use_game
@require_player
def end_turn(db, game, player):
	return logic.end_turn(db, game, player)

@post('/game/:game_id/purchase_road')
@use_db
@use_game
@require_player
def purchase_road(db, game, player):
	return logic.purchase_road(db, game, player)

@post('/game/:game_id/purchase_generator')
@use_db
@use_game
@require_player
def purchase_generator(db, game, player):
	return logic.purchase_generator(db, game, player)

@post('/game/:game_id/upgrade_generator')
@require_json('generator_type')
@use_db
@use_game
@require_player
def upgrade_generator(db, game, player):
	generator_type = request.json['generator_type']
	return logic.upgrade_generator(db, game, player, generator_type)

@post('/game/:game_id/trade')
@require_json('offering', 'requesting')
@use_db
@use_game
@require_player
def trade(db, game, player):
	offering = request.json['offering']
	requesting = request.json['requesting']
	return logic.trade(db, game, player, offering, requesting)

@post('/game/:game_id/log')
@require_json('message')
@use_db
@use_game
@require_player
def log(db, game, player):
	message = request.json['message']
	return logic.log(db, game, player, message)