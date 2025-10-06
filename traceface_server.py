#!/usr/bin/env python3

import eventlet
eventlet.monkey_patch()

import mimetypes
from os import path
import subprocess
import sys
import urllib.request

import eventlet.wsgi
from pigwig import PigWig, Response
import pigwig.exceptions

html = None
def root(request):
	return Response(html, content_type='text/html; charset=UTF-8')

traceface_dir = path.dirname(path.abspath(__file__))
chroot_dir = path.join(traceface_dir, 'chroot')
MB = 1024 * 1024
def trace(request):
	if len(request.body['paste']) > 0:
		return Response(code=303, location='/trace/' + request.body['paste'])
	code = request.body['code'].encode('utf-8')
	return _trace(code)

def trace_paste(request, paste):
	url = 'https://cpy.pt/raw/' + paste
	with urllib.request.urlopen(url) as r:
		if r.status != 200:
			try:
				content = r.read()
			except Exception:
				content = None
			raise pigwig.exceptions.HTTPException(500,
					b'%s: %d\n%s' % (url.encode('ascii'), r.status, content))
		code = r.read()
	return _trace(code)

def _trace(code):
	args = ['../nsjail/nsjail', '--use_cgroupv2', '--cgroupv2_mount', '/sys/fs/cgroup/NSJAIL',
			'-Mo', '--chroot', chroot_dir, '-E', 'LANG=en_US.UTF-8',
			'-R/lib', '-R/usr', '-R%s:/traceface' % traceface_dir, '-D/traceface',
			'--user', 'nobody', '--group', 'nogroup', '--time_limit', '2', '--disable_proc',
			'--iface_no_lo', '--cgroup_mem_max', str(50 * MB), '--cgroup_pids_max', '1', '--quiet',
			'--', '.venv/bin/python', '-q', 'traceface', '-s']
	print(' '.join(args))
	p = subprocess.run(args, input=code, capture_output=True, timeout=5)
	return Response(p.stdout, content_type='text/html; charset=UTF-8')

def static(request, filename):
	if not filename.endswith('.js') and not filename.endswith('.css'):
		return Response('not found', 404)
	try:
		with open(filename, 'rb') as f:
			content = f.read()
	except FileNotFoundError:
		return Response('not found', 404)
	content_type, _ = mimetypes.guess_type(filename)
	return Response(body=content, content_type=content_type)

routes = [
	('GET', '/', root),
	('POST', '/trace', trace),
	('GET', '/trace/<paste>', trace_paste),
	('GET', '/<filename>', static),
]

app = PigWig(routes)

if __name__ == '__main__':
	with open('server.html') as f:
		html = f.read()

	port = 8000
	if len(sys.argv) == 2:
		port = int(sys.argv[1])

	eventlet.wsgi.server(eventlet.listen(('127.1', port)), app)
