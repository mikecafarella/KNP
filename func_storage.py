# This function declares it is a “Relation-specific function” by requiring
# a Relation as its first parameter.
# It then takes a “”
import pickle
import marshal
import os
import types
from typing import Union, List, TypeVar 
import typing
import dill

if not os.path.exists('func_lib'):
	os.makedirs('func_lib')


class FuncTable:
	def __init__(self):
		self.table = {}
		

# Do Not directly use func_table in other files. 
# Since it will only be imported once.
func_table = FuncTable()

# persists locally
def store_func_table():
	func_table_copy = FuncTable()
	# Store all functions
	for k, v in func_table.table.items():
		with open("func_lib/"+k+"__code__", 'wb') as out_func:
			marshal.dump(v.fn.__code__, out_func)
		with open("func_lib/"+k+"__defaults__", 'wb') as out_func:
			pickle.dump(v.fn.__defaults__, out_func)
		with open("func_lib/"+k+"__closure__", 'wb') as out_func:
			pickle.dump(v.fn.__closure__, out_func)
		iscustomized = False
		istypingGen = False
		istypingUnion = False
		# print(v.typeSignature)
		# print(isinstance(v.typeSignature, type))
		for it in v.typeSignature:
			if not isinstance(it, type):
				iscustomized = True
		if iscustomized:
			if len(v.typeSignature) > 1:
				# print(len(v.typeSignature))
				raise Exception("not supporting more than one customized args")
			# try:
			# 	if v.typeSignature.__origin__ is typing.Union:
			# 		istypingUnion = True
			# except: 
			# 		pass
			# try:
			# 	if type(v.typeSignature) is typing.GenericMeta:
			# 		istypingGen = True
			# except: 
			# 	pass
		if iscustomized:
			with open("func_lib/"+ k +"__type__", 'wb') as out_func:
				dill.dump(v.typeSignature, out_func)
			func_table_copy.table[k] = FunctionWithSignature("dummy", "dummy", True)
		# elif istypingGen:
		# 	func_table_copy.table[k] = FunctionWithSignature("dummy", "istypingGen", True)
		else:
			func_table_copy.table[k] = FunctionWithSignature("dummy", v.typeSignature, True)

	with open("func_lib/func_table_store", 'wb') as out_table:
		pickle.dump(func_table_copy, out_table, -1)
	# DEBUG
	# with open("func_lib/func_table_store", 'rb') as in_table:
	# 	load_back = pickle.load(in_table)
	# 	print(type(load_back.table["strict_func"].typeSignature))


# load function table from local
def load_func_table():
	global func_table 
	if not os.path.exists('func_lib/func_table_store'):
		raise Exception("func_lib/func_table_store not exist")
	with open("func_lib/func_table_store", 'rb') as in_table:
		func_table = pickle.load(in_table)
		# print(func_table.table)
		for k, v in func_table.table.items():
			try:
				with open("func_lib/"+k+"__code__", 'rb') as in_func:
					marshaled_func = marshal.load(in_func)
				with open("func_lib/"+k+"__defaults__", 'rb') as out_func:
					pickled_arguments = pickle.load(out_func)
				with open("func_lib/"+k+"__closure__", 'rb') as out_func:
					pickled_closure = pickle.load(out_func)
				# print(v.typeSignature)
				# print(type(v.typeSignature))
			
				if v.typeSignature == "dummy":
					with open("func_lib/"+k+"__type__", 'rb') as out_func:
						v.typeSignature = dill.load(out_func)			
				v.fn = types.FunctionType(marshaled_func, globals(), k, pickled_arguments, pickled_closure)
			except OSError as e:
				raise Exception(e)
		# print(func_table.table)
	return func_table



def print_table():
	global func_table
	print("-----")
	# print(func_table)
	for k, v in func_table.table.items():
		print('%15s' % k, end='|')
		print('%50s' %v.fn, end='|')
		print(v.typeSignature)

	# print(func_table.table)
	print("-----")

# Current design is mandatory typeSignature
# Can use annotation 
def checkType(a, b):
	# print(type(a))
	# print(a)
	# print(type(b))
	# print(b)
	
	if type(a) is b:
		return True
	try:
		if b.__origin__ is typing.Union: # have several choices
			for i in b.__args__:
				if type(a) is i:
					return True
			return False
		elif b.__origin__ is typing.List: # list can only have one type
			if type(a) is list:
				for i in a:
					if type(i) is not b.__args__[0]:
						return False
				return True
			else:
				return False            
		elif b.__origin__ is typing.Tuple:
			if len(a) != len(b.__args__):
				return False
			if type(a) is tuple:
				for i, j in enumerate(a):
					if type(j) is not b.__args__[i]:
						return False
				return True
			else:
				return False
		elif b.__origin__ is typing.Dict: # all key value pairs should be the same
			if type(a) is dict:
				for k, v in a.items():
					if type(k) is not b.__args__[0] or type(v) is not b.__args__[1]:
						return False
				return True
			else:
				return False
	except:
		# print("Not using typing Union, List, Tuple, or Dict")
		pass
	try:
		if b.__verystrict__: # only this time b is an object
			return b.compare_type(a)
	except:
		# print("Not using customized class")
		pass
	return False

class FunctionWithSignature:
	def __init__(self, fn, typeSignature, reco = False):
		self.fn = fn
		
		self.typeSignature = typeSignature
		global func_table
		if not reco:
			func_table.table[str(self.fn.__name__)] = self
		# print_table()
	# Can directly call with invoke
	# Or call with applyTableFunction through table
	def invoke(self, *para):
		# print(self.typeSignature)
		# print(para)
		# print(type(para[0]))
		
		typedParams = zip(para, self.typeSignature)
		typeCheckResults = list(map(lambda x: checkType(x[0],x[1]), typedParams))
		if False in typeCheckResults:
			# raise Exception("Input parameters don't match type signature\nType Check Results: " + str(typeCheckResults))
			raise Exception("Input parameters don't match type signature")
		return self.fn(*para) # para is a tuple 


	# store in the function table
	# def store(self):
		# func_table.table[self.fn.__name__] = self

	



# publishedFunction = FunctionWithSignature(“createGDPOVerTimeVisualization”,
# 	[WikiDataType(“country”, ['Q6256']) 
#        WikiDataProperty(“gdp”, ['P2131', 'P2132']), 
#   WikiDataProperty(“timestamp”, ['P585'])],
# Lambda x: …..)


# The following method call makes no change to usgdp object. It just returns a new value
# niceViz = usgdp.applyTableFunction(['Country','gdp', ‘timestamp’], createGDPOverTimeVisualization)
def applyTableFunction(name, *arg):
	func_table.table[name].invoke(*arg)

