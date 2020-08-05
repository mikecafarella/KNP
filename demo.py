import kgpl
# The way our program works:
# If a dict, list or tuple contains a kgplvalue, it will 
# User A...
y = kgpl.value(10)
 
print(y) # should print 10
# At this moment, the central service has to store it and give it a URL
print(y.vid) # should have the special unique identifier for this value

# User A sends y.vid to User B.  It’s 0.

# User B:
aVal = kgpl.load_val(0)
print(aVal) # should print 10
 
bFavorite = kgpl.variable(aVal.vid)
# At this moment, there is a new Variable stored at the service.
# It has an outgoing edge "HasValue”, which points to the KGPLValue with
# URL <serverurl>/0
 
# Now what if we had something complicated?
newDict = {}
newDict["day_1-sales"] = 100
newDict["day-2-sales"] = aVal
 
b = kgpl.value(newDict)
print(b)
# This creates a new KGPLValue at the service. It has a URL.
# It is a dictionary. The dictionary has two entries. The first #‘day-1-sales’ has a value of type integer, with value 100. The second #‘day-2-sales’ has a value of type KGPLValue, with value #http://kgpl/92837472
 
# This publishes a variable called "Daily sales”, with KGPLvalue ‘b’
c = kgpl.variable(b.vid)

# Now on the next day….
sales = kgpl.load_var(c.vid)
newDict = kgpl.load_val(sales.val_id).getConcreteVal()
day3sales = kgpl.value(450)
newDict["day-3-sales"] = day3sales

kgpl.set_var(sales, kgpl.value(newDict).vid)
