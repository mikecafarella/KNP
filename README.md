# KNP

This is mainly the place listing the design desicions for our demo system.

## User Code

The user code consists of text references to the Action, and KG paragmeters. E.g. Compare USA.GDP Canada.GDP.

Currently, the compiler searches for the KG entity according to the KG reference using Wikidata's search tool, and picks the first result.

The user could go crazy on a KG reference such as Obama.wife.husband.wife.husband... Currently let's assume the KG reference won't contain more than two tokens.

## Slot Mapping

Slot mapping means a 1-to-1 mapping between KG data and the slots in the concrete method.

Currently slot mapping is hard-coded, but should be replaced in the future.

## Refinement

The most important infomation in a refinment are constraints. 

## Data Transformation

Once the compiler knows the slot mapping, it will transform the KG data to satisfy the input type requirement of the concrete method.




