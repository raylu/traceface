## using

`$ ./traceface -i re "re.match('[', 'a')"`

output: https://raylu.github.io/traceface/demo.html

alternatively,
```python
import traceface; traceface.set_trace()
some_code()
```

also,
```python
import traceface
with traceface.trace():
	some_code()
```

## developing

https://docs.python.org/3/library/sys.html#sys.settrace  
https://docs.python.org/3/reference/datamodel.html#frame-objects
