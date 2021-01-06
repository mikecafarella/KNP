# This function declares it is a “Relation-specific function” by requiring
# a Relation as its first parameter.
# It then takes a “”



Class FunctionWithSignature:
	def __init__(self, name, typeSignature, fn):
		…
		
	Def invoke(self, paramList):
		typedParams = zip(self.typeSignature, paramList)
		typeCheckResults = list(map(lambda x: x[1].checkType(x[0]), typedParams))
		if false in typeCheckResults:
			Raise Exception(“Input parameters don’t match type signature”)
		return fn.invoke(paramList)

publishedFunction = FunctionWithSignature(“createGDPOVerTimeVisualization”,
	[WikiDataType(“country”, ['Q6256']) 
       WikiDataProperty(“gdp”, ['P2131', 'P2132']), 
  WikiDataProperty(“timestamp”, ['P585'])],
Lambda x: …..)


# The following method call makes no change to usgdp object. It just returns a new value
niceViz = usgdp.applyTableFunction(['Country','gdp', ‘timestamp’], createGDPOverTimeVisualization)


