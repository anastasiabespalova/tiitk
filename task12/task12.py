import argparse
import json
import random
import numpy as np
import sys
from itertools import product
import sys

def parse_float(p):
	p = p.split("/")
	if len(p) > 1:
		p = float(p[0]) / float(p[1])
	else:
		p = float(p[0])
	return p


parser = argparse.ArgumentParser()
parser.add_argument("--N", default=None)
parser.add_argument("--source", default=None)
parser.add_argument("--regime", default='1')
parser.add_argument("--R", default=None)
parser.add_argument("--epsilon", default=None)
parser.add_argument("--q", default=None)
parser.add_argument("--out_file", default='code.txt')
args = parser.parse_args()

N = args.N
source = args.source

regime = None

if (N != "None") and not (N is None):
	N = int(N)

model = None
with open(source, 'r') as f:
	model = dict(json.load(f))

switches = model['switches']
models = model['models']
seq = model['source']
if len(seq) > 1:
	raise Exception("More than one switch. Possibly unstationary process!")

# Entropy
actual_switch = switches[seq[-1]]
keys = actual_switch.keys()
base_probs = [parse_float(actual_switch[k]) for k in keys]
probs = [{k_:parse_float(models[k][k_]) for k_ in models[k].keys()} for k in keys]

res = dict()
for i, p in enumerate(probs):
	for k in p.keys():
		if k in res.keys():
			res[k] += p[k] * base_probs[i]
		else:
			res[k] = p[k] * base_probs[i]

entropy = sum(-res[k]*np.log2(res[k]) for k in res.keys())
D = sum(res[k]*(np.log2(res[k]) ** 2) for k in res.keys()) - entropy ** 2
if args.regime == '1':
	print('Entropy:', entropy)
	sys.exit()

# regime 2
q = int(args.q)
R = float(args.R)
e = float(args.epsilon)

if R < entropy:
	raise Exception('Code doesn\'t exist! (R < Entropy)')

flag_break = False
for i in range(1, 23):
	if q < i * R:
		margin = (D / (i * e)) ** 0.5
		l_margin = entropy - margin
		r_margin = entropy + margin
		w_list = list()
		for j in range(2 ** i):
			b_j = np.binary_repr(j, i)
			prob = 1
			for b_j_i in b_j:
				prob *= res[b_j_i]
			mean = -np.log2(prob) / i
			if (mean <= r_margin) and (l_margin <= mean):
				w_list += [b_j]
		if R * i >= np.log2(len(w_list)):
			flag_break = True
			break

if not flag_break:
	raise Exception('Out of time!')
m = int(np.ceil(R * i / np.log2(q)))
num = int(np.ceil(np.log2(q)))
blocks = [np.binary_repr(j, num) for j in range(2**num)]
def get_block_word(j, q, blocks, m):
	res = []
	while j != 0:
		res += [blocks[j % q]]
		j = j // q
	res += ([blocks[0]] * (m - len(res)))
	return res[::-1]
with open(args.out_file, 'w') as f:
	f.write('n = {}\n'.format(i))
	f.write('m = {}\n'.format(m))
	for j, w in enumerate(w_list):
		f.write('{} {}\n'.format(w, get_block_word(j, q, blocks, m)))
