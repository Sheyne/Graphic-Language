from pydot import Dot, Edge
import re
from itertools import tee
from uuid import uuid4

def uniqueid():
	return str(uuid4())

def tokenize(sentence, tokenizer=re.compile(r'\w+|[\!\.\?]')):
	return tokenizer.findall(sentence)

def pairwise(iterable):
	a, b = tee(iterable)
	b.next()
	return zip(a,b)

class Graph(object):
	def __init__(self, sentence):
		self.dot = Dot()
		self.parse_sentence(sentence)

	def add(self, word1, word2):
		self.dot.add_edge(Edge(word1, word2))
		return word1
		
	def instantiate(self, word):
		return self.add(uniqueid(), word)
	
	def parse_sentence(self, sentence):
		for word1, word2 in pairwise(map(self.instantiate,tokenize(sentence))):
			self.add(word1, word2)
	
			
g = Graph('the cat climbs the tree when the dog chases it')
g.dot.write_png('test.png')