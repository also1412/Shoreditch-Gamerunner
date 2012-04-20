##########
### Game logic for actually running a game
##########
from uuid import uuid4
import random
from copy import copy

import communication
import config

from bottle import abort

import thread


def setup_player(player):
	in_game_player = {
		"id": uuid4().hex,
		"player": player['id'],
		"endpoint": player['endpoint'],
		"generators": copy(config.DEFAULT_GENERATORS),
		"improved_generators": copy(config.DEFAULT_GENERATORS),
		"resources": copy(config.DEFAULT_RESOURCES),
		"roads": 0
	}

	return in_game_player

def run_generators(players):
	for player in players.values():
		for generator in player['generators']:
			for i in range(player['generators'][generator]):
				if random.randint(1, 10) == 1:
					player['resources'][config.GENERATORS[generator]] += 1
		for generator in player['improved_generators']:
			for i in range(player['improved_generators'][generator]):
				if random.randint(1, 10) == 1:
					player['resources'][config.GENERATORS[generator]] += 2

def start_game(db, players):
	print "Starting game"
	game_id = uuid4().hex

	game = {
		"id": game_id,
		"players": {},
		"player_order": [],
		"round": 0
	}

	for player in players:
		p = setup_player(player)
		game['players'][p['id']] = p
		game['player_order'].append(p['id'])

	generators_to_use = copy(config.GENERATORS.keys())
	random.shuffle(generators_to_use)

	p = 0
	max_generators = 0

	# First pass out all generators as evenly as possible
	while (len(generators_to_use) > 0):
		game['players'][game['player_order'][p]]['generators'][generators_to_use.pop()] += 1

		total_generators = sum(game['players'][game['player_order'][p]]['generators'].values())

		if total_generators > max_generators:
			max_generators = total_generators

		p += 1
		if p == len(game['player_order']):
			p = 0

	# Now ensure everyone has an equal amount
	generators_to_use = copy(config.GENERATORS.keys())
	random.shuffle(generators_to_use)

	for p in game['players']:
		while sum(game['players'][p]['generators'].values()) < max_generators:
			game['players'][p]['generators'][generators_to_use.pop()] += 1

	started_players = []

	for player in game['players'].values():
		response, data = communication.request(player, "game/%s" % (player['id']), {"player": player, "endpoint": "http://localhost:8080/game/%s" % game_id}, 'PUT')
		if response.status != 200:
			for p in started_players:
				communication.request(player, "cancel_game", {"player": player})
			return False
		started_players.append(player)

	db.save(game)

	next_turn(db, game)
	return True

def next_turn(db, game):
	turn_taken = False
	while not turn_taken: # Find the next player ready to make a move
		print "Starting turn"
		game['turn'] = game.get('turn', -1) + 1

		if game['turn'] >= len(game['player_order']):
			# Next round
			game['round'] += 1
			game['turn'] = 0

			print "Starting round %i" % game['round']

			if game['round'] >= config.MAX_ROUNDS:
				return end_game(game)

		run_generators(game['players'])

		player = game['players'][game['player_order'][game['turn']]] # Wow - nice line

		response, data = communication.request(player, "game/%s/start_turn" % player['id'])

		db.save(game)

		if response.status == 200:
			turn_taken = True
		else:
			print "Turn skipped"

def require_player_turn(f):
	def inner_func(*args, **kwargs):
		return f(*args, **kwargs)
	return inner_func

def has_enough_resources(player, resources):
	for resource in resources:
		if player['resources'][resource] < resources[resource]:
			return False
	return True

def require_resources(resources):
	def require_resources_inner(f):
		def inner_func(db, game, player, *args, **kwargs):
			if not has_enough_resources(player, resources):
				abort(400, 'Not enough %s' % resource)
			return f(db, game, player, *args, **kwargs)
		return inner_func
	return require_resources_inner

def charge_resources(player, resources):
	for resource in resources:
		player['resources'][resource] -= resources[resource]

@require_player_turn
def end_turn(db, game, player):
	def run_end_turn():
		next_turn(db, game)
	print "Ended turn"
	thread.start_new_thread(run_end_turn, ())
	return {"status": "success"}

def end_game(game):
	print "THE GAME HAS ENDED"
	for player in game['players'].values():
		print "Player %s(%s)" % (player['id'], player['player'])
		print "Resources"
		print "========="
		for resource in player['resources']:
			print "	%s:	%s" % (resource, player['resources'][resource])
		print "========="
		print "Generators"
		print "========="
		for generator in player['generators']:
			print "	%s:	%s" % (generator, player['generators'][generator])
		print "========="
		print "Roads:	%s" % player['roads']
		communication.request(player, "game/%s" % player['id'], method="DELETE")

@require_player_turn
@require_resources(config.ROAD_COST)
def purchase_road(db, game, player):
	charge_resources(player, config.ROAD_COST)
	player['roads'] += 1
	db.save(game)
	return {"player": player}

@require_player_turn
@require_resources(config.GENERATOR_COST)
def purchase_generator(db, game, player):
	# TODO: Check not over the limit
	charge_resources(player, config.GENERATOR_COST)

	generator = random.choice(config.GENERATORS.keys())
	player['generators'][generator] += 1

	db.save(game)
	return {"player": player, 'generator_type': generator}

@require_player_turn
def trade(db, game, player, offering, requesting):
	if not has_enough_resources(player, offering):
		abort(400, "You don't have enough stuff!")

	players = [game['players'][p] for p in game['player_order'] if not p == player['id']]
	random.shuffle(players) # Don't give one person first refusal

	print "Player ", player['id'], " offering ", offering, " for ", requesting

	for p in players:
		print "Other has ", p['resources']
		if has_enough_resources(p, requesting):
			print "HAS ENOUGH"
			response, data = communication.request(p, "game/%s/trade" % player['id'], {"player": player, "offering": offering, "requesting": requesting})
			if response.status == 200:
				print "WAS ACCEPTED"
				charge_resources(player, offering)
				charge_resources(p, requesting)

				for resource in offering:
					p['resources'][resource] += offering[resource]

				for resource in requesting:
					player['resources'][resource] += requesting[resource]

				db.save(game)
				return {"player": player}

	abort(500, "No bites")