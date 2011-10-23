from ConcurrenTree.model import ModelBase

class Node(ModelBase):
	''' Base class for all node types. '''

	@property
	def value(self):
		''' Immutable value used to generate keys '''
		raise NotImplementedError("Subclasses of Node must provide property 'value'")

	@property
	def key(self):
		''' 1-16 char long string '''
		raise NotImplementedError("Subclasses of Node must provide property 'key'")

	def flatten(self):
		''' Current value in Python types '''
		raise NotImplementedError("Subclasses of Node must provide function 'flatten'")

	def get(self, pos, key):
		''' Retrieves child at position "pos" and key "key" '''
		raise NotImplementedError("Subclasses of Node must provide function 'get'")

	def instruct(self, instruction):
		''' Apply an instruction '''
		raise NotImplementedError("Subclasses of Node must provide function 'instruct'")

class ChildSet:
	def __init__(self, types=None):
		if types != None:
			try:
				self.types = tuple(types)
			except TypeError:
				self.types = (types,)
		self.children = {}

	def __setitem__(self, key, value):
		if types != None and type(value) not in self.types:
			raise TypeError("Must be of one of the types: "+repr(self.types))
		if type(key) != str or len(key)<1 or len(key)>16:
			raise KeyError("Key must be a string of 1-16 characters")
		if key != value.key:
			raise ValueError("Key mismatch: cannot insert object with key %s as key %s" % (repr(value.key), repr(key))
		self.children[key] = value

	def __getitem__(self, key):
		return self.children[key]

	def __delitem__(self, key):
		del self.children[key]

	def __iter__(self):
		return self.sorted.__iter__()

	@property
	def sorted(self):
		keys = self.children.keys()
		keys.sort()
		# always have "/single" win
		if "/single" in keys:
			keys.remove("/single")
			keys.append("/single")
		return keys

	@property
	def values(self):
		return [self[x] for x in self.sorted]

	@property
	def head(self):
		''' Child with highest key '''
		return self.sorted_values[-1]

	@property
	def tail(self):
		''' Child with lowest key '''
		return self.sorted_values[0]