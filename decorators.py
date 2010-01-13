def decorator(func):
	def sub(*args, **kwargs):
		return func(*args, **kwargs)
	return sub

def sanitizeArgs(func):
	if func.func_code.co_flags & 8: # Has **var
		return func # Can't know what arguments it takes
	accepts = func.func_code.co_varnames[:func.func_code.co_argcount]
	
	def sub(*args, **kwargs):
		return func(*args, **dict((key, val) for key, val in kwargs.items() if key in accepts))
	
	return sub

@decorator
def callableGenerator(func, *args, **kwargs):
	generator = func(*args, **kwargs)
	def callable(*args):
		if len(args) == 0:
			return generator.next()
		elif len(args) == 1:
			return generator.send(args[0])
		else:
			return generator.send(args)
	return callable
