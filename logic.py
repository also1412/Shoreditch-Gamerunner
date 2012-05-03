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

import pusher

pusher.app_id = config.PUSHER_APP_ID
pusher.key = config.PUSHER_KEY
pusher.secret = config.PUSHER_SECRET

def push(game, subject, content):
	game['pushes'].append([subject, content])
	p = pusher.Pusher()
	p['game-' + game['id']].trigger(subject, content)

def setup_player(player):
	in_game_player = {
		"id": uuid4().hex,
		"secret": uuid4().hex,
		"player": player['id'],
		"name": player['id'],
		"endpoint": player['endpoint'],
		"generators": copy(config.DEFAULT_GENERATORS),
		"improved_generators": copy(config.DEFAULT_GENERATORS),
		"resources": copy(config.DEFAULT_RESOURCES),
		"pr": 0,
		"customers": 0
	}

	return in_game_player

def run_generators(players):
	awarded = {}

	def award(player, generator, amount=1):
		generated = config.GENERATORS[generator]
		player['resources'][generated] += 1

		if not player['id'] in awarded:
			awarded[player['id']] = {"name": player['player'], "resources": {}}
		if not generated in awarded[player['id']]["resources"]:
			awarded[player['id']]["resources"][generated] = 0

		awarded[player['id']]["resources"][generated] += amount

	for player in players.values():
		for generator in player['generators']:
			for i in range(player['generators'][generator]):
				if random.randint(1, 10) == 1:
					award(player, generator)
		for generator in player['improved_generators']:
			for i in range(player['improved_generators'][generator]):
				if random.randint(1, 10) == 1:
					award(player, generator, 2)
	return awarded

def start_game(db, name, players):
	print "Starting game"
	game_id = uuid4().hex

	game = {
		"id": game_id,
		"name": name,
		"players": {},
		"player_order": [],
		"turn": len(players),
		"round": 0,
		"pushes": []
	}

	used_names =[]

	for player in players:
		p = setup_player(player)
		i = 0
		while p['name'] in used_names:
			i += 1
			p['name'] = p['player'] + ' %i' % i
		used_names.append(p['name'])
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
	return game_id

def game_is_over(game):
	if game['round'] >= config.MAX_ROUNDS:
		return True

	for player in game['players'].values():
		if player['customers'] >= config.MAX_POINTS:
			return True

	return False

def next_turn(db, game):
	turn_taken = False
	while not turn_taken: # Find the next player ready to make a move
		game['turn'] = game['turn'] + 1

		if game['turn'] >= len(game['player_order']):
			# Next round
			game['round'] += 1
			game['turn'] = 0

			if game_is_over(game):
				return end_game(game)

			print "Starting round %i" % game['round']
			game['player_order'].reverse()

			generated = run_generators(game['players'])
			if len(generated.keys()) > 0:
				push(game, 'new-round', {'round': game['round'], 'players': copy(game['players']), "generated": generated})
			else:
				push(game, 'new-round', {'round': game['round'], 'players': copy(game['players'])})


		player = game['players'][game['player_order'][game['turn']]] # Wow - nice line

		response, data = communication.request(player, "game/%s/start_turn" % player['id'])

		db.save(game)

		if response.status == 200:
			turn_taken = True
			push(game, 'start-turn', {'player': player, 'turn': game['turn'], 'round': game['round']})
		else:
			push(game, 'turn-skipped', {'player': player, 'turn': game['turn'], 'round': game['round']})

def require_player_turn(f):
	def inner_func(db, game, player, *args, **kwargs):
		if player['id'] != game['player_order'][game['turn']]:
			abort(400, 'It is not your turn')
		return f(db, game, player, *args, **kwargs)
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
				abort(400, 'Not enough resources')
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

def award_bonus_points(game):
	max_pr = 0
	for player in game['players'].values():
		if player.get('pr',0) > max_pr:
			max_pr = player['pr']
	
	for player in game['players'].values():
		if player.get('pr') == max_pr:
			player['customers'] += 2
			push(game, 'award-bonus', {"customers": 2, "player": player})

def end_game(game):
	award_bonus_points(game)

	def sort_players(player_id):
		return int(game['players'][player_id]['customers'])

	game['player_order'] = sorted(game['player_order'], key=sort_players, reverse=True)

	push(game, 'end', {"players": [game['players'][p] for p in game['player_order']]})

	for player in game['players'].values():
		communication.request(player, "game/%s" % player['id'], method="DELETE")

@require_player_turn
@require_resources(config.PR_COST)
def purchase_pr(db, game, player):
	charge_resources(player, config.PR_COST)
	player['pr'] += 1
	db.save(game)
	push(game, 'purchase-pr', {"round": game['round'], "turn": game['turn'], "player": player})
	return {"player": player}

@require_player_turn
@require_resources(config.GENERATOR_COST)
def purchase_generator(db, game, player):
	if sum(player['generators'].values()) >= config.MAX_RESOURCE_GENERATORS:
		abort(400, "You can't build any more generators")

	charge_resources(player, config.GENERATOR_COST)

	generator = random.choice(config.GENERATORS.keys())
	player['generators'][generator] += 1

	player['customers'] += 1

	db.save(game)

	push(game, 'purchase-generator', {"round": game['round'], "turn": game['turn'], "player": player, 'generator_type': generator})
	return {"player": player, 'generator_type': generator}

@require_player_turn
@require_resources(config.GENERATOR_IMPROVEMENT_COST)
def upgrade_generator(db, game, player, generator_type):
	if sum(player['improved_generators'].values()) >= config.MAX_IMPROVED_RESOURCE_GENERATORS:
		abort(400, "You can't build any more generators")

	if player['generators'][generator_type] < 1:
		abort(400, "You don't have enough %s" % generator_type)

	charge_resources(player, config.GENERATOR_IMPROVEMENT_COST)

	player['generators'][generator_type] -= 1
	player['improved_generators'][generator_type] += 1

	player['customers'] += 1

	db.save(game)

	push(game, 'upgrade-generator', {"round": game['round'], "turn": game['turn'], "player": player, 'generator_type': generator_type})
	return {"player": player, 'generator_type': generator_type}

@require_player_turn
def trade(db, game, player, offering, requesting):
	if not has_enough_resources(player, offering):
		abort(400, "You don't have enough stuff!")

	players = [game['players'][p] for p in game['player_order'] if not p == player['id']]
	random.shuffle(players) # Don't give one person first refusal

	print "Player ", player['id'], " offering ", offering, " for ", requesting

	trade_id = uuid4().hex

	push(game, 'trade', {"round": game['round'], "turn": game['turn'], "player": player, 'offering': offering, 'requesting': requesting, "trade_id": trade_id})

	for p in players:
		if has_enough_resources(p, requesting):
			response, data = communication.request(p, "game/%s/trade" % player['id'], {"player": player, "offering": offering, "requesting": requesting})
			if response.status == 200:
				charge_resources(player, offering)
				charge_resources(p, requesting)

				for resource in offering:
					p['resources'][resource] += offering[resource]

				for resource in requesting:
					player['resources'][resource] += requesting[resource]

				push(game, 'trade-accepted', {"trade_id": trade_id, "player": p})

				db.save(game)



				return {"player": player}

	# No bites, see if it's good enough for a bank trade

	if sum(offering.values()) >= (sum(requesting.values()) * config.BANK_TRADE_RATE):
		# The bank will take the trade
		charge_resources(player, offering)
		for resource in requesting:
			player['resources'][resource] += requesting[resource]

		push(game, 'trade-bank-accepted', {"trade_id": trade_id})

		db.save(game)

		return {"player": player}

	push(game, 'trade-rejected', {"trade_id": trade_id})
	abort(500, "No bites")

@require_player_turn
def log(db, game, player, message):
	push(game, 'log', {'player': player, 'message': message})