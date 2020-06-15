import sys
from bin_tree import BinaryTree, Leaf 
import json

regime = 'code'
f_name = sys.argv[1]

if f_name[-4:] == '.zmh':
	regime = 'decode'
if regime == 'code':
	symbols = []
	counts = dict()
	with open(f_name, 'rb') as f:
		byte = f.read(1)
		while byte:
			if byte in counts.keys():
				counts[byte] += 1
			else:
				counts[byte] = 1
			symbols.append(byte)
			byte = f.read(1)

	counts = sorted([(k, counts[k]) for k in counts.keys()], key=lambda x: x[1])
	priority_row = [Leaf(i[0], i[1]) for i in counts]

	while len(priority_row) != 1:
		btree = None
		if isinstance(priority_row[0], Leaf):
			btree = BinaryTree(priority_row[0]).merge(priority_row[1])
		else:
			btree = priority_row[0].merge(priority_row[1])
		priority_row = priority_row[2:]
		i = 0
		for e in priority_row:
			if e.priority >= btree.priority:
				break
			i += 1
		priority_row.insert(i, btree)

	final_btree = priority_row[0]
	codes = dict(final_btree.get_codes())

	out_sequence = ''
	for s in symbols:
		out_sequence += codes[s] 
	out = []
	#l = len(out_sequence)
	#for i in range(l // 8 + ((l % 8) != 0)):
	#	out.append(out_sequence[i * 8: (i + 1) * 8])
	#last_byte_len = len(out[-1])
	#out_sequence = ''
	#for o in out:
	#	print(o)
	#	out_sequence += chr(int(o, base=2))
	#out_sequence += chr(last_byte_len)
	new_codes = {codes[k]: ord(k) for k in codes.keys()}
	codes_s = json.dumps(new_codes)
	with open(f_name + '.zmh', 'w') as f:
		f.write(out_sequence + '\n')
		f.write(codes_s)
else:
	inputs = []
	with open(f_name, 'r') as f:
		for l in f:
			inputs.append(l)
	#inp = ''
	#for i in inputs[:-1]:
	#	inp += (i + '\n')
	to_decode_str = inputs[0][:-1]
	codes = json.loads(inputs[1])
	#last_byte_len = ord(to_decode[-1])
	#to_decode = [bin(ord(c))[2:] for c in to_decode[:-1]]
	#to_decode = [('0'*(8-len(c))) + c for c in to_decode]	
	#to_decode[-1] = to_decode[-1][-last_byte_len:]
	#to_decode_str = ''
	#for b in to_decode:
	#	to_decode_str += b

	class LilBinT:
		def __init__(self):
			self.subt = [None, None]
		def get_subtree(self, code):
			return self.subt[int(code)]
		def put_val(self, val, code):
			side = int(code[0])
			if len(code) == 1:
				self.subt[side] = val
			else:
				if self.subt[side] is None:
					self.subt[side] = LilBinT()
				self.subt[side].put_val(val, code[1:])
	tree = LilBinT()
	for k in codes.keys():
		tree.put_val(codes[k], k)
	out_sequence = []
	cur_tree = tree
	for c in to_decode_str:
		cur_tree = cur_tree.get_subtree(c)
		if not isinstance(cur_tree, LilBinT):
			out_sequence.append(cur_tree)
			cur_tree = tree
	with open(f_name[:-4], 'wb') as f:
		for o in out_sequence:
			f.write(bytes([o])) 
