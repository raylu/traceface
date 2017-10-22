import atexit
import copy
from os import path
import sys

import jinja2

tf_dir = path.dirname(path.abspath(__file__))

def set_trace():
	if sys.gettrace() is not None:
		return
	tracer = Tracer()
	atexit.register(tracer.write_output)
	sys.settrace(tracer.trace_dispatch)

def trace():
	return TraceContextManager()

class TraceContextManager:
	def __init__(self):
		self.tracer = None

	def __enter__(self):
		if sys.gettrace() is not None:
			return
		self.tracer = Tracer()
		sys.settrace(self.tracer.trace_dispatch)

	def __exit__(self, exc_type, exc_value, traceback):
		if self.tracer is None:
			return
		sys.settrace(None)
		self.tracer.write_output()

class Tracer:
	def __init__(self):
		self.trace = []
		self.bottom_frame = None

	def run(self, code, run_globals=None):
		sys.settrace(self.trace_dispatch)
		try:
			exec(code, run_globals)
		finally:
			sys.settrace(None)

	def trace_dispatch(self, frame, event, arg):
		if event == 'call':
			self.handle_call(frame)
			return self.trace_dispatch
		elif event == 'exception':
			self.handle_exception(frame)

	def handle_call(self, frame):
		if self.bottom_frame is None:
			self.bottom_frame = frame
		elif frame.f_back is not self.bottom_frame: # skip the first 2 frames
			self._add_trace(frame.f_back)

	def handle_exception(self, frame):
		if frame is not self.bottom_frame:
			self._add_trace(frame, filter=True)

	def _add_trace(self, frame, filter=False):
		local_vars = frame.f_locals
		code = frame.f_code
		line_no = frame.f_lineno
		first_line_no = code.co_firstlineno
		depth = -1
		while frame is not None and frame is not self.bottom_frame:
			frame = frame.f_back
			depth += 1
		frame_obj = Frame(code.co_filename, code.co_name, line_no, first_line_no, depth, local_vars)
		if filter and frame_obj in self.trace: # don't add frames for exceptions bubbling up
			return
		self.trace.append(frame_obj)

	def write_output(self):
		trace = self.trace
		for frame in trace:
			frame.context()

		with open(path.join(tf_dir, 'template.jinja2'), 'r') as f:
			template = jinja2.Template(f.read(), autoescape=True, trim_blocks=True, lstrip_blocks=True)
		output_path = path.join(tf_dir, 'trace.html')
		with open(output_path, 'w') as f:
			stream = template.stream({'trace': trace})
			stream.enable_buffering()
			stream.dump(f)
		print('trace written to', output_path)

class Frame:
	files = {}

	def __init__(self, filepath, func_name, line_no, first_line_no, depth, local_vars):
		self.filepath = filepath
		self.func_name = func_name
		self.line_no = line_no
		self.first_line_no = first_line_no
		self.depth = depth
		self.local_vars = {k: repr(v) for k, v in local_vars.items()}

		self.context_lines = None
		self.call_index = None
		self.def_index = None

	def context(self):
		if self.filepath[0] == '<': # <module>, <string>
			return
		lines = self.files.get(self.filepath)
		if lines is None:
			with open(self.filepath, 'r') as f:
				lines = f.readlines()
				for i, line in enumerate(lines):
					lines[i] = line.rstrip('\r\n')
				self.files[self.filepath] = lines
		# get 3 lines of context
		start = max(self.line_no - 4, 0)
		self.context_lines = copy.copy(lines[start:self.line_no + 3])
		self.call_index = self.line_no - start - 1
		if self.first_line_no != self.line_no: # <genexpr>, <listcomp>, <setcomp>, <dictcomp>
			if self.first_line_no - 1 >= start:
				self.def_index = self.first_line_no - start - 1
			else:
				self.context_lines.insert(0, lines[self.first_line_no - 1])
				self.def_index = 0
				self.call_index += 1

	def __repr__(self):
		return '%s(%r, %r, %r, %r, %r, %r)' % (self.__class__.__name__, self.filepath, self.func_name,
											   self.line_no, self.first_line_no, self.depth, self.local_vars)

	def __eq__(self, other):
		if not isinstance(other, Frame):
			return False
		our_key = (self.filepath, self.func_name, self.line_no)
		other_key = (other.filepath, other.func_name, other.line_no)
		return our_key == other_key
