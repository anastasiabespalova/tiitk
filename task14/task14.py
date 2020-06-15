import argparse
import numpy as np
from itertools import combinations
import json
import math
import random

parser = argparse.ArgumentParser()
parser.add_argument("--r", default=None)
parser.add_argument("--n", default=None)
parser.add_argument("--p", default=None)
parser.add_argument("--regime", default=None)

parser.add_argument("--code", default='code_info.json')
parser.add_argument("--m", default=None)
parser.add_argument("--e", default=None)

parser.add_argument("--y", default=None)

args = parser.parse_args()

def read_params(file_name):
	with open(file_name, 'r') as f:
		to_save = json.load(f)	
		n = to_save['n']
		t = to_save['t']
		r = to_save['r']
		res_G = np.array(to_save['G'])
		code_words = {tuple(i[0]): i[1] for i in to_save['CW']}
		syn_dict = {tuple(i[0]): i[1] for i in to_save['SD']}
	return n, t, r, res_G, code_words, syn_dict


def random_bin_vector(l):
	while True:
		v = np.random.randint(0, 2, l)
		if v.sum() > 0:
			return v

def bin_repr(k):
	for i in range(2 ** k):
		yield [int(e) for e in np.binary_repr(i, k)] 

def comb(i, n):
	f = math.factorial
	return (f(n) / f(n - i)) / f(i)

if args.regime == 'generate':
	n = int(args.n)
	r = int(args.r)
	p = float(args.p)
	t = int(p * n)
	d = 2 * t + 1
	k = n - r
	res = 0
	for i in range(1, d - 1):
		res += comb(i, n)
	if res >= 2 ** r:
		 raise Exception('Linear code may not exist!')

	G_eye = np.eye(k)
	H_eye = np.eye(n - k)
	C = list()
	C += [list(random_bin_vector(n - k))]
	for i in range(1, k):
		combs = C.copy()
		for j in range(1, min(d - 1, i + 1)):
			for c in combinations(C, j):
				combs.append((np.array(c).sum(axis=0) % 2).tolist())
		while True:
			v = random_bin_vector(n - k).tolist()
			if not (v in combs):
				C.append(v)
				break
	C = np.vstack(np.array(C))
	res_H = np.hstack([C.T, H_eye])
	res_G = np.hstack([G_eye, C])
	res_p = 1 - sum([comb(i, n) * (p ** i) * ((1 - p) ** (n - i)) for i in range(t)])
	print('Error probability {}'.format(round(p, 10)))
	code_words = {tuple(((br @ res_G) % 2)): br for br in bin_repr(k)}
	syn_dict = dict()
	for br in bin_repr(n):
		syn = tuple((br @ res_H.T) % 2)
		if syn in syn_dict.keys():
			syn_dict[syn] += [br]
		else:
			syn_dict[syn] = [br]
	
	with open(args.code, 'w') as f:
		to_save = dict()
		to_save['n'] = n
		to_save['t'] = t
		to_save['r'] = r
		to_save['G'] = res_G.tolist()
		to_save['CW'] = [(k, code_words[k]) for k in code_words.keys()]
		to_save['SD'] = [(k, syn_dict[k]) for k in syn_dict.keys()]
		json.dump(to_save, f)		

elif args.regime == 'code':
	m = np.array([int(m_i) for m_i in args.m])
	e = args.e
	n, t, r, res_G, code_words, _ =  read_params(args.code)
	if len(m) != (n - r):
		raise Exception('Message lenth != {}!'.format(n - r))
	if e is None:
		t_ = np.random.randint(0, t + 1)
		e = np.zeros(n, dtype=int)
		inds = random.sample(list(range(len(m))), t_ - 1)
		e[inds] = 1
	else:
		e = np.array([int(e_i) for e_i in e])
		if e.sum() > t:
			raise Exception('Error weight > t')
	print('Code result:', ((m @ res_G) + e) % 2 )
	print('Error:', e)
elif args.regime == 'decode':
	n, t, r, reg_G, code_words, syn_dict  =  read_params(args.code)
	y = [int(y_i) for y_i in args.y]
	for k in syn_dict.keys():
		if y in syn_dict[k]:
			syndrome = k
	error = min(syn_dict[syndrome], key=lambda x: sum(x))
	print('Error:', error)	
	m = tuple((np.array(error) + np.array(y)) % 2)
	real_m = code_words[m]
	print('Message:', real_m)
	alpha = {i: 0 for i in range(n)}
	for k in code_words.keys():
		alpha[sum(k)] += 1
	p = float(args.p)
	p_res = 0
	for i in range(n):
		p_res += alpha[i] * (p ** i) * ((1 - p) ** (n - i))
	p_res = 1 - p_res
	print('Error probability: {}'.format(p_res))
