import ORM_modified
from ORM_modified import createRelation
import kgpl
import pandas as pd
import matplotlib.pyplot as plt
r = createRelation("Q515")
r.extend("P31",True,"Cities")
r.changeFocus("Cities")
r.extend("P1082",False,"population")
r.query()
r.df.population = r.df.population.astype('double')
val = kgpl.value(r, comment="cities with their population", user="Wendy")
df = val.getConcreteVal().df
df1 = df[df["population"] == 89.2]
print(df1)
print(df)
"""
df = r.df
df1 = df[df["population"] > 1000]
df2 = df[(df["population"] <= 1000) & (df["population"] > 800)]
df3 = df[(df["population"] <= 800) & (df["population"] > 500)]
df4 = df[(df["population"] <= 500) & (df["population"] > 300)]
df5 = df[(df["population"] <= 300) & (df["population"] > 100)]
df6 = df[df["population"] <= 100]
print(df1.shape, df2.shape, df3.shape, df4.shape, df5.shape, df6.shape)
"""
hist = df.hist(bins=5, column=["population"], range=[0, 1e6])
plt.savefig("histogram.jpg")
val = kgpl.value(kgpl.Image("histogram.jpg"), comment="histogram of cities", user="Wendy", dependency=[val])