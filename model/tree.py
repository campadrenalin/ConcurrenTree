from ConcurrenTree.model import ModelBase
from ConcurrenTree.util.hasher import key, sum

def sort(d):
	k = d.keys()
	k.sort()
	return k

class Tree(ModelBase):
	def __init__(self, value="", name=''):
		''' Do not manipulate children externally. Use class methods. '''
		self.name = name
		self.initroot()
		self._value = value
		self._length = len(value)
		self._deletions = [False] * len(self)
		self._children = []
		self.operations = {}
		for i in range(len(self)+1):
			self._children.append(dict())

	def initroot(self):
		self.initplace(None, 0, "root")

	def initplace(self, parent, level, shortcut):
		self._parent = parent
		self._level = level
		self._shortcut = shortcut

	def insert(self, pos, value):
		''' Insert a child to the tree with string "value" at position "pos" '''
		result = Tree(value)
		self.insert_tree(pos, result)
		return result

	def delete(self, pos):
		''' Mark a character in a tree as deleted '''
		del self[pos]

	def insert_tree(self, pos, obj):
		''' Insert an object as a child tree, setting its era properties '''
		obj.initplace(self, self.level+1, self._shortcut)
		self._children[pos][obj.key] = obj

	def get(self, pos, key):
		''' Return the subtree with key "key" from position "pos" '''
		return self._children[pos][key]

	def all_children(self):
		''' 
		Returns a dict (keyed on position) of sorted child hash lists.
		'''
		results = {}
		for i in range(self._length+1):
			hashes = self.children(i)
			if hashes:
				results[i] = hashes
		return results

	def children(self, i):
		''' A sorted list of all children at position i. '''
		return [self.get(i, child) for child in sort(self._children[i])]

	def __getitem__(self, i):
		return self._value[i]

	def __getslice__(self, i, j):
		if j > len(self): j = len(self)
		return [self[x] for x in range(i, j)]

	def __delitem__(self, i):
		self._deletions[i] = True

	def __delslice__(self, i, j):
		for x in range(i,j):
			del self[x]

	def __len__(self):
		''' Return the length of the internal immutable string '''
		return self._length

	# Era functions and utilities

	def up(self, num):
		if num==0:
			return self
		else:
			return self._parent.up(num-1)

	@property
	def parent(self):
		return self._parent

	@property
	def level(self):
		return self._level

	@property
	def era(self):
		return self.level // 16

	@property
	def shortcut(self):
		return self.era, self._shortcut

	@property
	def shortcutparent(self):
		return self.up(self.level % 16)

	@property
	def is_root(self):
		return self.level==0

	@property
	def root(self):
		return self.up(self.level)

	def find(self, shortcut):
		''' Resolve a shortcut into a tree. '''
		shortcut = validate_shortcut(shortcut)

	@property
	def address(self):
		sp = self.shortcutparent
		if self.era == 0:
			# no shortcut
			pass
		else:
			# shortcut
			pass

	def flatten(self):
		''' Returns a string that summarizes self and all descendants. Not backwards-compatible for applying ops. '''
		rstring = ""
		for i in range(self._length+1):
			for c in self.children(i):
				rstring += c.flatten()
			if i < self._length:
				# check whether to include character at this position
				if not self._deletions[i]:
					rstring += self._value[i]
		return rstring

	def trace(self, pos):
		''' 
		Given a position in the flat text, compute an (address, position) pair.
		'''
		t = self._trace(pos)
		if type(t) == tuple:
			return t
		else:
			raise IndexError("%d is out of range" % pos)

	def _trace(self, pos):
		togo = pos
		for i in range(len(self)+1):
			for child in self.children(i):
				x = child._trace(togo)
				print "///",x
				if type(x) == tuple:
					return [[i, child.key]]+x[0], x[1]
				else:
					togo -= x
			if togo == 0:
				return ([],i)
			if i < len(self) and not self._deletions[i]:
				togo -=1
		return togo

	def proto(self):
		''' Return a protocol representation '''
		runningstring = ""
		deletions = []
		result = []
		for i in range(len(self)+1):
			for child in self.children(i):
				if runningstring:
					result.append(runningstring)
					runningstring = ""
				result.append(child.proto())
			if i < len(self):
				runningstring += self._value[i]
				if self._deletions[i]: deletions.append(i)
		if runningstring: result.append(runningstring)
		result.append(deletions)
		return result

	@property
	def key(self):
		return key(self._value)

def from_proto(obj, era=None):
	if type(obj)==dict:
		value = None
		shortcut = obj['address']
		if "value" in obj:
			value = tree_from_proto(obj['value'])
		return TreeReference(era, [int(shortcut[0][1:]), shortcut[1]], value)
	children = {}
	value =""
	deletions = obj.pop()
	for x in obj:
		if type(x)==str:
			value+=x
		else:
			pos = len(value)
			if not pos in children:
				children[pos]=[]
			children[pos].append(from_proto(x, era))
	tree = Tree(value)
	for pos in children:
		for child in children[pos]:
			tree.insert_tree(pos, child)
	return tree


def validate_shortcut(shortcut):
	try:
		if (type(shortcut) in (str, unicode)):
			shortcut = shortcut.split("#")
		assert(type(shortcut)==list or type(shortcut)==tuple)
		assert(len(shortcut)==2)
		assert(type(shortcut[0])==int and shortcut[0]>=0)
		assert(type(shortcut[1]) in (str, unicode))
	except AssertionError:
		raise InvalidShortcutError(shortcut)
	return shortcut

# An older implementation of eras used the classes below.
# I tore most of the code out but this part was too good
# and took too much work, so I'm keeping it for now on
# the remote chance we need it again, so I won't have to
# recode it again. ~ Philip

class TreeReference(dict):
	''' 
		An object that acts as a proxy for an actual tree,
		using an era to request the tree on the fly. Treat it
		like a regular old Tree object, but be forewarned that
		those functions may raise ShortcutUnresolvedErrors if
		the era can't resolve the shortcut to a Tree.
	'''
	def __init__(self, era, shortcut, tree=None):
		super(TreeReference, self).__init__()
		self.era = era
		self.shortcut = validate_shortcut(shortcut)
		if tree!=None:
			self.set(tree)

	def __getattr__(self, attr):
		if attr in dir(Tree):
			return getattr(self.tree, attr)
		else:
			if attr in self:
				return self[attr]
			else:
				raise AttributeError(attr)

	def __setattr__(self, attr, value):
		if attr in dir(Tree):
			setattr(self.tree, attr, value)
		else:
			self[attr] = value

	def __repr__(self):
		return "<tree.TreeReference instance: %s>" % str(self.shortcut)

	def proto(self):
		return {"address":["#"+str(self.shortcut[0]), self.shortcut[1]]}

	@property
	def tree(self):
		return self.era.resolve(self.shortcut)

	def set(self, tree):
		self.era.insert(self.shortcut, tree)

class ShortcutError(Exception): pass
class InvalidShortcutError(ShortcutError): pass
class ShortcutUnresolvedError(ShortcutError): pass
