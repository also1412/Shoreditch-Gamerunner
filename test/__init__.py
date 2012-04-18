import json
from uuid import uuid4

from httplib2 import Http

from config import PORT

http = Http()

def request(resource, method='GET', body=None, headers={"Content-type": "application/json"}, testing=True):
	if body and not isinstance(body, basestring):
		body['testing'] = testing
		body = json.dumps(body)

	return http.request("http://localhost:%i/%s" % (PORT, resource), method=method, body=body, headers=headers)

def clear_db():
	request('test/clear', 'POST')

def create_player():
	player_data = {
		"name": uuid4().hex,
		"endpoint": "http://example.com/"
	}

	response, data = request('player', 'POST', player_data)

	return json.loads(data)['player']