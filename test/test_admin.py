import unittest
from uuid import uuid4
from test import request
import json

class AdminTest(unittest.TestCase):
	def test_register(self):
		player_data = {
			"name": uuid4().hex,
			"endpoint": "http://example.com/"
		}

		response, data = request('player', 'POST', player_data)
		assert response.status == 201, (response, data)

		player = json.loads(data)['player']

		assert 'id' in player, player
		assert 'secret' in player, player
		assert player['name'] == player_data['name'], player
		assert player['endpoint'] == player_data['endpoint'], player

	def test_cant_register_without_name_or_endpoint(self):
		player_data = {
			"name": uuid4().hex,
		}

		response, data = request('player', 'POST', player_data)
		assert response.status == 400, (response, data)

		player_data = {
			"endpoint": uuid4().hex,
		}

		response, data = request('player', 'POST', player_data)
		assert response.status == 400, (response, data)

	def test_register_with_id(self):
		player_data = {
			"id": uuid4().hex,
			"name": uuid4().hex,
			"endpoint": "http://example.com/"
		}

		response, data = request('player', 'POST', player_data)
		assert response.status == 201, (response, data)

		player = json.loads(data)['player']

		assert player['id'] == player_data['id'], (response, data)