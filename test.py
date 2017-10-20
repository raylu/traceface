#!/usr/bin/env python3

def hello():
	for i in range(2):
		shout('hello')

def shout(s):
	try:
		say(s.upper())
	except:
		raise Exception('whoops')

def say(s):
	raise Exception(s)
