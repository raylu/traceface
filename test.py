#!/usr/bin/env python3

def hello():
	gen = (shout('hello') for _ in range(2))
	next(gen)

def shout(s):
	try:
		say(s.upper())
	except:
		raise Exception('whoops')

def say(s):
	raise Exception(s)
