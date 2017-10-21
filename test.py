#!/usr/bin/env python3

def hello():
	gen = (shout(s) for s in ['hello', 'bye'])
	list(gen)

def shout(s):
	try:
		say(s.upper())
	except:
		raise Exception('whoops')

def say(s):
	print(s)
	if s == 'BYE':
		raise Exception(s)
