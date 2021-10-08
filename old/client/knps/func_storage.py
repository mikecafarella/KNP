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

# Current design is mandatory typeSignature
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
	# Can directly call with invoke
	def invoke(self, *para):
		typedParams = zip(para, self.typeSignature)
		typeCheckResults = list(map(lambda x: checkType(x[0],x[1]), typedParams))
		if False in typeCheckResults:
			raise Exception("Input parameters don't match type signature")
		return self.fn(*para) # para is a tuple 
