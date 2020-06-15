class Leaf:
	def __init__(self, elem, weight):
		self.elem = elem
		self.priority = weight

	def get_codes(self):
		return [[self.elem, '']]

class BinaryTree:
	def __init__(self, element):
		self.left = element 
		self.priority = element.priority
		self.right = None

	def merge(self, item):
		if self.right is None:
			self.right = item
			self.priority += self.right.priority
			return self
		else:
			return BinaryTree(self).merge(item)

	def get_codes(self):
		code_table = []
		codes_l = [[i[0], '0' + i[1]] for i in self.left.get_codes()]
		codes_r = []
		if not (self.right is None):
			codes_r = [[i[0], '1' + i[1]] for i in self.right.get_codes()]
		return codes_l + codes_r 
