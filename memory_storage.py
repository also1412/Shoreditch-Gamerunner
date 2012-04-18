#########
### Just store stuff in memory - not pretty but it'll be fine for this use
#########

from uuid import uuid4

class MemoryStorage(object):
	def __init__(self):
		self.docs = {}
		self.types = {}

	def save(self, doc):
		if not 'id' in doc:
			doc['id'] = uuid4().hex
		self.docs[doc['id']] = doc

		if 'type' in doc:
			if doc['type'] not in self.types:
				self.types[doc['type']] = {}

			self.types[doc['type']][doc['id']] = doc

	def get_by_type(self, doc_type):
		if doc_type not in self.types:
			return []
		return self.types[doc_type].values()

	def empty(self):
		self.docs = {}
		self.types = {}


memory_storage = MemoryStorage()

# decorator to add the DB to arguments
def use_db(f):
	def inner_func(*args, **kwargs):
		return f(memory_storage, *args, **kwargs)
	return inner_func