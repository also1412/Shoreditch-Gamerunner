#########
### Just store stuff in memory - not pretty but it'll be fine for this use
#########

from uuid import uuid4

class MemoryStorage(object):
	def __init__(self):
		self.docs = {}

	def save(self, doc):
		if not 'id' in doc:
			doc['id'] = uuid4().hex
		self.docs[doc['id']] = doc


memory_storage = MemoryStorage()

# decorator to add the DB to arguments
def use_db(f):
	def inner_func(*args, **kwargs):
		return f(memory_storage, *args, **kwargs)
	return inner_func