#!/usr/bin/env python3

import eventlet
eventlet.monkey_patch()

import mimetypes
from os import path
import subprocess
import sys

import eventlet.wsgi
from pigwig import PigWig, Response

html = None
def root(request):
	return Response(html, content_type='text/html; charset=UTF-8')

traceface_dir = path.dirname(path.abspath(__file__))
chroot_dir = path.join(traceface_dir, 'chroot')
MB = 1024 * 1024
def trace(request):
	code = request.body['code'].encode('utf-8')
	args = ['../nsjail/nsjail', '-Mo', '--chroot', chroot_dir, '-E', 'LANG=en_US.UTF-8',
			'-R/usr', '-R/lib', '-R/lib64', '-R%s:/traceface' % traceface_dir, '-D/traceface',
			'--time_limit', '2', '--disable_proc', '--iface_no_lo',
			'--cgroup_mem_max', str(50 * MB), '--cgroup_pids_max', '1', '--quiet', '--',
			'/usr/bin/python3', '-q', 'traceface', '-s']
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
