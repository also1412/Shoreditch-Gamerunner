from copy import copy

from bottle import request
from bottle import abort


def require_json(*fields):
	def require_json_inner(f):
		def inner_func(*args, **kwargs):
			if not 'json' in kwargs:
				if not request.json:
					abort(400, 'Must use Content-type of application/json')
				kwargs['json'] = request.json

			for field in fields:
				if not field in kwargs['json']:
					abort(400, 'Must pass "%s"' % field)
			return f(*args, **kwargs)
		return inner_func
	return require_json_inner

# Remove sensitive data from a document
def sanitise(doc):
	doc = copy(doc)
	del doc['secret']
	return doc
