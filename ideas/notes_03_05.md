# Sample KGP Code, March 5, 2020



## Example 1

In the codebase:
---
CompareGDP(gdp1: GDP, gdp2:GDP): __Image__ {
  assert(gdp1.unit == gdp2.unit)
  return PlotTimeSeries(gdp1, gdp2)
}
---

User actions:
---
CompareGDP(USA.gdp, China.gdp)
---

Result: the system sends GDP data to PlotTimeSeries(), returns an
Image.

Requirements:  The "GDP" type is well-defined and can detect the
"gdp" property.  In the KG, we'll have:

(USA, gdp, <TableOfData>)
(China, gdp, <TableOfData>)


The "type generation process" yields a virtual type for:

- Every node in the KG is a potential type.  Politician is a good
  example.
- GDP is also a node in the KG.  So I guess it's a potential type.
-


The KG Type Synthesizer emits data of this form:
---
(Typename, isMemberOfType(val))
---

It emits millions of items:
- (Politician, isMemberOfPoliticianType(v))
- (Person, isMemberOfPersonType(v))
- (BarackObama, isMemberOfBarackObamaType(v))
- ...

When building isMemberOfPoliticianType() classifier, the system can
use lots of different evidence:
- instance-of properties
- profession properties
- overlap in properties between known and unknown members of the
  class.

-------------------------------------------------
We see this:  (Obama, instance-of, Politician)
We don't see this:  (Dataset, instance-of, GDP)

Instead we see: (USA, has-gdp, Dataset)

-------------------------------------------------

def generateAllTypes(inputRawKG) {
  allTypes = []
  for node in inputRawKG.getNodes():
    allTypes.append((node.getName(), synthesizeMembershipClassifier(node)))
  }
}

def generateAllTypes(inputRawKG) {
  allTypes = []
  for node in inputRawKG.getNodes():
    if node.isNoun() and node.isNotProperNoun() {
      allTypes.append((node.getName(), synthesizeMembershipClassifier(node)))
    }
  }
}


Conclusions:
-- Every node in KG is a potential type
-- Type classifiers are not created until someone uses it for the
   first time
-- In the short-term, programmers cannot create custom types.  The
   only way to add a type is to add a new node to the KG.  We will
   revisit this decision in a few months, because it will probably
   make some programs harder to write.   

----------------------------------------------------------

Consider this code again:
---
CompareGDP(gdp1: GDP, gdp2:GDP): __Image__ {
  assert(gdp1.unit == gdp2.unit)
  return PlotTimeSeries(gdp1, gdp2)
}
---

CompareGDP(USA.gdp, Canada.gdp)
CompareGDP(USA, Canada)

We don't really love but we will allow:
---
CompareGDP(country1: Country, country2:Country): __Image__ {
  assert(country1.gdp.unit == country2.gdp.unit)
  return PlotTimeSeries(country1.gdp1, country2.gdp2)
}
---


Compare(USA, Canada)


CompareLandmass(USA, Canada)
CompareGDP(USA, Canada)
CompareMovieIndustries(USA, Canada)
CompareTotalSumOfFreshWater(USA, Canada)
CompareHeight(USA, Canada)


Conclusions, Part 1:
-- Every node in KG is a potential type
-- Type classifiers are not created until someone uses it for the
   first time
-- In the short-term, programmers cannot create custom types.  The
   only way to add a type is to add a new node to the KG.  We will
   revisit this decision in a few months, because it will probably
   make some programs harder to write.   

Conclusions, Part 2:
-- Functions should be written with the "most specific relevant
   type".  If you're comparing GDP, then use the GDP type.  Don't use
   the country type!
-- The system will do automatic type coercion when the user provides
   an imperfect type match.
-- It's still legal to define CompareGDP(Country, Country), but it's
   probably a bad idea if you're just going to call Country.gdp().



