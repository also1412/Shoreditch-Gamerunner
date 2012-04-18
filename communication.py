###########
## Communication with players
###########
import json

from httplib2 import Http

def request(player, resource, body=None, method='POST'):
	http = Http()
	if body and not isinstance(body, basestring):
		body = json.dumps(body)

	return http.request("%s/%s" % (player['endpoint'], resource), method=method, body=body, headers={"Content-type": "application/json"})