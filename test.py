#!/usr/bin/env python3

def hello():
	for i in range(2):
		shout('hello')

def shout(s):
	say(s.upper())

def say(s):
	print(s)

if __name__ == '__main__':
	hello()
