###########
## Communication with players
###########
import json

from httplib2 import Http

def request(player, resource, body=None):
	http = Http()
	if body and not isinstance(body, basestring):
		body = json.dumps(body)

	return http.request("%s/%s" % (player['endpoint'], resource), method='POST', body=body, headers={"Content-type": "application/json"})