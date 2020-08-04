from typing import List
from dateutil import parser as dateparser

from knpl import Entity, Property, KNProgramSpace, KGPLFunction
from kgdata import KGData
import knpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import HTML


def plotTimeSeries(entities: List[Entity], prop: Property):
    pName = kgdata.wd.name
    pTime = kgdata.wd.P585
    fig, axs = plt.subplots()
    axs.set_xlabel("Time")
    axs.set_ylabel(prop.get(pName))
    axs.set_title(prop.get(pName)) 
    for e in entities:
        tuples = []
        for x in e.getRelation(prop):
            try:
                d = dateparser.parse(str(x.get(pTime)))
                y = float(x.get(prop))
                tuples.append((d, y))
            except Exception:
                pass
        tuples.sort()
        xvals = list(map(lambda t: t[0], tuples))
        yvals = list(map(lambda t: t[1], tuples))
        axs.plot(xvals, yvals, label=e.label())
    axs.legend()
    fig.show()


def compare(entities: List[Entity], prop: Property):
    pName = kgdata.wd.name


    labels = []
    vals = []
    for e in entities:
        l = e.label()
        v = e.getBestSingleton(prop, ignoreNone=True)
        if v is not None:
            labels.append(l)
            vals.append(v)

    plt.rcdefaults()
    x = np.arange(len(labels))
    fig, axs = plt.subplots()
    axs.bar(x, vals)
    axs.set_xticks(x)
    axs.set_xticklabels(labels)
    axs.set_title(prop.label())
    fig.show()
    




kgdata = KGData(KNProgramSpace("http://141.212.113.104:7200/repositories/2"))

def search(searchStr, limit=10):
    rst = kgdata.wd.finder.search_entity(searchStr, limit=limit)
    rst.extend(kgdata.wd.finder.search_property(searchStr, limit=limit))
    d = {}
    d["id"] = ["kgdata.wd." + str(x.get("id", "")) for x in rst]
    d["label"] = [x.get("label", "") for x in rst]
    d["description"] = [x.get("description", "") for x in rst]
    return pd.DataFrame(data=d)


def search_e(searchStr, limit=10):
    rst = kgdata.wd.finder.search_entity(searchStr, limit=limit)
    d = {}
    d["id"] = ["kgdata.wd." + str(x.get("id", "")) for x in rst]
    d["label"] = [x.get("label", "") for x in rst]
    d["description"] = [x.get("description", "") for x in rst]
    return pd.DataFrame(data=d)
    

def search_p(searchStr, limit=10):
    rst = kgdata.wd.finder.search_property(searchStr, limit=limit)
    d = {}
    d["id"] = ["kgdata.wd." + str(x.get("id", "")) for x in rst]
    d["label"] = [x.get("label", "") for x in rst]
    d["description"] = [x.get("description", "") for x in rst]
    return pd.DataFrame(data=d)


def showAll(es, ps):
    image = kgdata.wd.P18
    
    d = {}
    d["label"] = [e.label() for e in es]
    d["uri"] = [e.entityUri for e in es]
    d["image"] = [e.getBestSingleton(image, ignoreNone=True) for e in es]
    for p in ps:
        d[p.label()] = [e.getBestSingleton(p, ignoreNone=True) for e in es]

    df = pd.DataFrame(data=d)
    def image_formatter(url):
        return f'<img width=100 src="{url}">'

    allProps = ["label"]
    allProps.extend(["uri"])    
    allProps.extend([p.label() for p in ps])
    allProps.extend(["image"])

    return HTML(df[allProps].to_html(formatters={"image": image_formatter}, escape=False))


def show(e):
    label = e.label()
    image = kgdata.wd.P18
    
    d = {"label": [e.label()], "image": [e.getBestSingleton(image, ignoreNone=True)]}
    df = pd.DataFrame(data=d)
    def image_formatter(url):
        return f'<img width=100 src="{url}">'

    return HTML(df[["label", "image"]].to_html(formatters={"image": image_formatter}, escape=False))


