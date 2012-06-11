from itertools import tee
from functools import wraps

def pairwise(l):
	" For each consecutive pair of values in `l` yeild the pair."
	x, y = tee(l)
	y.next()
	for pair in zip(x,y):
		yield pair

def pairwiseargs(n=0, generatormode=False, allresultspass=None):
	"""
	A decorator that does pairwise arguments. A function can be passed any number of arguments, and decorated function will be called with each pair as augments. 
	
	`n` arguments at the beginning of a function carry through, so:

	>>> @pairwiseargs(n=1)
	... def test(a,b,c):
	...     print a, ":", b, c
	... 
	>>> test(1,2,3,4)
	1 : 2 3
	1 : 3 4

	If generator mode is true, the decorated function becomes a generator with each value it returns yielded.
	
	If allresultspass is not None, and allresultspass(each of the return values of the decorated function) is not Trueish, return False. 
	"""
	def internal(f):
		@wraps(f)
		def intpair(*args):
			z = args[:n]
			for pair in pairwise(args[n:]): 
				yield f(*(z+pair))
		if generatormode:
			return intpair
		else: 
			@wraps(f)
			def _(*args):
				for res in intpair(*args):
					if allresultspass is not None and not allresultspass(res):
						return False
					elif res is not None:
						return res
			return _			
	return internal

class Graph(object):
	def __init__(self, *args):
		" Initialize the graph. call self.add(*args)"
		self.edges = ({}, {})
		self._nodes = None
		self.add(*args)
				
	def getbucket(self, idx, a):
		"""
		If idx is 0:
			Gets the set of nodes that a points at; it is referred to as the "forwards" bucket. 
		If idx is 1:
		   	Gets the set of nodes pointing at a; it is referred to as the "backwards" bucket
		"""
		edx = self.edges[idx]
		try:
			bucket = edx[a]
		except KeyError:
			bucket = set()
			edx[a] = bucket
		return bucket
	
	def getbuckets(self, a, b):
		' Returns a tuple containing both the "forwards" and "backwards" buckets. '
		return self.getbucket(0, a), self.getbucket(1, b)
	
	@pairwiseargs(1)
	def add(self, a, b):
		"""
		Adds arguments to the graph as edges by pairs.
		
		ex:
			`add(1,2,3)` is equivalent to `add(1,2)` and `add(2,3)`
		"""
		ba, bb = self.getbuckets(a,b)
		ba.add(b)
		bb.add(a)
		self._nodes = None

	@pairwiseargs(1)
	def remove(self, a, b):
		"""
		Pairwise removes the arguments from the graph. Each pair is assumed to be an edge.
		
		ex:
			`remove(1,2,3)` is equivalent to `remove(1,2)` and `remove(2,3)`
		"""
		try:
			ba, bb = self.getbuckets(a,b)
			ba.remove(b)
			bb.remove(a)
		except KeyError:
			raise(KeyError(a,b))
		else:
			if not ba:
				del self.edges[0][a]
			if not bb:
				del self.edges[1][b]
		self._nodes = None
	
	@pairwiseargs(1, allresultspass=lambda res: res)
	def hasedge(self, a, b):
		'Checks if the graph contains the edge (a, b), where (a, b) is each of the arguments pairwise. '
		try:
			b in self.edges[0][a]
			return True
		except KeyError: pass
	
	def items(self, direction=0):
		"Generate a tuple for each edge in the graph. If direction is 1 do so with the nodes in the edge flipped. "
		return ((k, v)
					for k, vs in self.edges[direction].items()
						for v in vs)
	
	def potentialcompliments(self, node, dir=0):
		try:
			return self.edges[dir][node]
		except KeyError:
			return set()
	
	def bigitems(self):
		for edge in self.items():
			for compliment_dir, node in enumerate(reversed(edge)):
				compliment = edge[compliment_dir], compliment_dir
				yield edge, node, compliment
				
	def unify(self, target, items=None, solutions=[], potential_solution={}):
		if items is None:
			items = self.bigitems()
		try:
			edge, node, compliment = items.next()
		except StopIteration:
			print "Adding", potential_solution
			solutions.append(potential_solution)
		else:
			if isvariable(node):
				if isvariable(compliment[0]):
					print "Oh noes"
				values = tuple(value for value in target.potentialcompliments(*compliment)
							if node.matches(value))
				for value, iter in zip(values, tee(items, len(values))):
					mysolution = potential_solution.copy()
					mysolution[node] = value
					print node,":", value, mysolution
					self.unify(target, items, potential_solution=mysolution)
			elif isvariable(compliment[0]):
				print "I'll deal with this later. ", node, compliment
				self.unify(target, items, potential_solution=potential_solution)
			elif compliment[1] == 0 and target.hasedge(edge):
				print "Nice 'n normal. "
				self.unify(target, items, potential_solution=potential_solution)
		return solutions
				

def isvariable(a):
	return isinstance(a, Variable)

class Variable(object):
	variable_counter = 0
	def __init__(self):
		self.unique_num = Variable.variable_counter
		Variable.variable_counter += 1
	
	def matches(self, val):
		return True
	
	def __repr__(self):
		return "%s(%d)" % (self.__class__.__name__, self.unique_num)

class Anonymous(Variable):
	def matches(self, val):
		return isanonymous(val)


if __name__ == "__main__":
	g = Graph(*xrange(6))
	g.add(1, 100)
	v = Variable()
	g2 = Graph(1, v, 3)
	print g2.unify(g)
	