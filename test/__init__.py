import json
from httplib2 import Http

def request(resource, method='GET', body=None, headers={"Content-type": "application/json"}, testing=True):
	if body and not isinstance(body, basestring):
		body['testing'] = testing
		body = json.dumps(body)

	return http.request("http://localhost/%s" % resource, method=method, body=body, headers=headers)