##########
### Game logic for actually running a game
##########
from uuid import uuid4
import random
from copy import copy

import communication
import config


def setup_player(player):
	in_game_player = {
		"id": uuid4().hex,
		"player": player['id'],
		"endpoint": player['endpoint'],
		"generators": copy(config.DEFAULT_GENERATORS),
		"improved_generators": [],
		"resources": copy(config.DEFAULT_RESOURCES),
		"roads": 0
	}

	for i in range(config.DEFAULT_GENERATOR_NUMBER):
		in_game_player['generators'][random.choice(config.GENERATORS.keys())] += 1

	return in_game_player

def run_generators(players):
	for player in players.values():
		for generator in player['generators']:
			if random.randint(1, 10) == 1:
				print player['resources']
				player['resources'][config.GENERATORS[generator]] += 1
		for generator in player['improved_generators']:
			if random.randint(1, 10) == 1:
				player['resources'][config.GENERATORS[generator]] += 2

def start_game(db, players):
	print "Starting game"
	game_id = uuid4().hex

	game = {
		"id": game_id,
		"players": {},
		"player_order": []
		"turn_count" = 0
	}

	for player in players:
		p = setup_player(player)
		game['players'][p['id']] = p
		game['player_order'].append(p['id'])

	started_players = []

	for player in game['players'].values():
		response, data = communication.request(player, "game/%s/%s" % (game_id, player['id']), {"player": player}, 'PUT')
		if response.status != 200:
			for p in started_players:
				communication.request(player, "cancel_game", {"player": player})
			return False
		started_players.append(player)

	db.save(game)

	next_turn(game)
	return True

def next_turn(game):
	print "Starting turn"
	game['turn'] = game.get('turn', -1) + 1

	run_generators(game['players'])

	player = game['players'][game['player_order'][game['turn']]] # Wow - nice line

	communication.request(player, "start_turn", {"player": player})