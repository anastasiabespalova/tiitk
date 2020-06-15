import argparse
import json
import random
import numpy as np
import keyboard
import sys


def generate_seq(N, model, switches, verbose=True):
	seq = []
	i = 0
	while True:
		for s in model['source']:
			if keyboard.is_pressed('q'):
				sys.exit()
			if N == i:
				break
			m = get_random(switches[s])
			c = get_random(models[m])
			if verbose:
				print(c)
			if not (N is None):
				i += 1
				seq.append(c)
		if N == i:
			break
	if not (N is None):
		return seq
		
	

def parse_float(p):
	p = p.split("/")
	if len(p) > 1:
		p = float(p[0]) / float(p[1])
	else:
		p = float(p[0])
	return p


def get_random(d):
	d_ = [(e[0], parse_float(e[1])) for e in zip(d.keys(), d.values())]
	p = random.random()
	thr = 0
	for e in d_:
		thr += e[1]
		if p <= thr:
			return e[0]

parser = argparse.ArgumentParser()
parser.add_argument("--N", default=None)
parser.add_argument("--source", default=None)
parser.add_argument("--seq", default=None)
args = parser.parse_args()

N = args.N
source = args.source
seq = args.seq

regime = None

if seq is None:
	regime = 1
else:
	regime = 2

if (N != "None") and not (N is None):
	N = int(N)
model = None
with open(source, 'r') as f:
		model = dict(json.load(f))
switches = model['switches']
models = model['models']

if regime == 1:
	generate_seq(N, model, switches)
if regime == 2:
	seq = seq.split(',')
	samples = generate_seq(N, model, switches, False)
	items, counts = np.unique(samples, return_counts=True)
	probs = counts / counts.sum()
	dist = dict(zip(list(items), list(probs)))
	prob = 1
	for s in seq:
		if s in dist.keys():
			prob *= dist[s]
		else:
			prob = 0
			break
	print('Sequence probability estimation:', prob)
	
