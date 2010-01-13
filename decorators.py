def decorator(func):
	"""
	This is a meta-decorator to facilitate decorator creation.  When used on a
	function, it returns a function which, when called, passes the decorated
	function and the arguments of the call to the decorator.
	
	Example:
	
		@decorator
		def test(func, *args, **kwargs):
			print 'Function %r called with arguments %r and %r' % (func, args, kwargs)
			return func(*args, **kwargs)
		
		@test
		def foo(bar):
			print 'Foo', bar
		
		foo(5)
	
	Prints:
	
		Function <function foo at 0x021A20F0> called with arguments (5,) and {}
		Foo 5
	"""
	def sub(subfunc):
		def sub2(*args, **kwargs):
			return func(subfunc, *args, **kwargs)
		return sub2
	return sub

def sanitizeArgs(func):
	"""
	This decorator will look at the arguments accepted by a function and cuts out
	unhandled arguments.  This should be used by other decorators if the function
	to be decorated has its argument names inspected.  In the case of frameworks 
	like Pylons, argument names are inspected to modify what information is pulled
	from requests; this will be skewed by other decorators and cause all parameters
	to be passed.  If this decorator is used, extraneous arguments will be culled.
	
	Example:
	
		@decorator
		def test(func, *args, **kwargs):
			func = sanitizeArgs(func)
			return func(*args, **kwargs)
		
		@test
		def foo():
			print 'Test'
		
		foo(5, foo='bar')
	
	Prints:
	
		Test
	"""
	if func.func_code.co_flags & 8: # Has **var
		return func # Can't know what arguments it takes
	accepts = func.func_code.co_varnames[:func.func_code.co_argcount]
	
	def sub(*args, **kwargs):
		return func(*args, **dict((key, val) for key, val in kwargs.items() if key in accepts))
	
	return sub

@decorator
def callableGenerator(func, *args, **kwargs):
	"""
	When used on a generator function, this decorator wraps the generator object
	in a callable wrapper equivalent to next/send with handling for multiple
	arguments.
	
	Example:
	
		@callableGenerator
		def test():
			print 'Initial'
			yield
			print 'Second call'
			value = yield
			print 'Third call', value
			a, b = yield
			print 'Fourth call', a, b
		
		generator = test()
		generator()
		generator('foo')
		generator('foo', 'bar')
	
	Prints:
	
		Initial
		Second call
		Third call foo
		Fourth call foo bar
	"""
	func = sanitizeArgs(func)
	generator = func(*args, **kwargs)
	generator.next()
	def callable(*args):
		try:
			if len(args) == 0:
				return generator.next()
			elif len(args) == 1:
				return generator.send(args[0])
			else:
				return generator.send(args)
		except StopIteration:
			return None
	return callable
