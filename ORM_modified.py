# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

import sys
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import numpy as np

endpoint_url = "https://query.wikidata.org/sparql"
item = "item"


class Relation:
    """
    The class returned when createRelation is called.
    It contains string field with query.
    We call Relation.query when we need to do the query.
    """
    def __init__(self, entity_id: str, property_id: str, isSubject: bool, limit: int, rowVerbose: bool, colVerbose: bool, time_property: str, time: str, name: str):
        self.entity_id = entity_id
        self.query_str = ""
        self.dic = {}
        self.result_dic = {"Entity ID": []}
        self.df = pd.DataFrame()
        self.count = 0
        self.verbose_count = 0
        self.time_property = time_property
        self.time = time
        self.limit = limit
        self.focus = "Entity ID"
        self.trace = pd.DataFrame()
        if property_id:
            self.extend(property_id, isSubject, name, rowVerbose, colVerbose, limit, time_property, time)

    def query(self):
        if self.query_str == "":
            self.result_dic = {"Entity ID": ['http://www.wikidata.org/entity/' + str(self.entity_id)]}
            return self.result_dic
        results = get_results(endpoint_url, self.query_str)
        result_dict = {"Entity ID": ['http://www.wikidata.org/entity/' + str(self.entity_id)]}
        for i in range(1, self.count + 1):
            result_dict[self.dic[i]["name"]] = []
            if self.dic[i]["colVerbose"]:
                for key, value in self.dic[i]["property_name_dic"].items():
                    result_dict[self.dic[i]["name"] + "_" + value] = []
        # TODO: Fix the following
        if self.dic[i]["colVerbose"] and not self.dic[i]["rowVerbose"]:
            for key, value in result_dict.items():
                if key in results['results']['bindings'][0].keys():
                    result_dict[key].append(results['results']['bindings'][0][key]['value'])
                else:
                    result_dict[key].append(None)
            # idx = result_dict[self.dic[i]["name"]+"_2"].index(max(result_dict[self.dic[i]["name"]+"_2"]))
            # result_dict[self.dic[i]["name"]+"_2"] = [max(result_dict[self.dic[i]["name"]+"_2"])]
            # result_dict[self.dic[i]["name"]] = [result_dict[self.dic[i]["name"]][idx]]
        else:
            for result in results['results']['bindings']:
                for key, value in result_dict.items():
                    if key in result.keys():
                        result_dict[key].append(result[key]['value'])
                    else:
                        result_dict[key].append(None)

        result_dict["Entity ID"] = ['http://www.wikidata.org/entity/' + str(self.entity_id)] * len(result_dict[self.dic[self.count]["name"]])
        self.result_dic = result_dict
        self.df = pd.DataFrame.from_dict(self.result_dic)
        return self.df

    def extend(self, property_id: str, isSubject: bool, name: str, rowVerbose=False, colVerbose=False, limit=None, time_property=None, time=None):
        self.count += 1
        self.dic[self.count] = {}
        self.dic[self.count]["name"] = name
        self.dic[self.count]["focus"] = self.focus
        self.dic[self.count]["property_id"] = property_id
        self.dic[self.count]["isSubject"] = isSubject
        self.dic[self.count]["limit"] = limit
        self.dic[self.count]["rowVerbose"] = rowVerbose
        self.dic[self.count]["colVerbose"] = colVerbose
        self.dic[self.count]['time_property'] = time_property
        self.dic[self.count]['time'] = time
        if rowVerbose or colVerbose:
            self.verbose_count += 1
            self.dic[self.count]["verbose_count"] = self.verbose_count
            self.dic[self.count]["property_name_dic"] = self.search_property_for_verbose(self.verbose_count)
        if time_property and time:
            self.time_property = time_property
            self.time = time
        if limit:
            self.limit = limit
        self.query_str = self.define_query_relation()
        self.generate_trace()

    def changeFocus(self, name="Entity ID"):
        self.focus = name

    def define_query_relation(self):

        rdf_triple, time_filter, limit_statement = """""", """""", """"""

        if self.count < 1:
            return None

        for i in range(1, self.count + 1):
            if self.dic[i]["rowVerbose"] or self.dic[i]["colVerbose"]:
                if self.dic[i]["focus"] == "Entity ID":
                    rdf_triple += """wd:""" + self.entity_id + """ p:""" + self.dic[i]['property_id'] + """ ?statement""" + str(self.dic[i]['verbose_count']) + """.""" + \
                                """?statement""" + str(self.dic[i]['verbose_count']) + """ ps:""" + self.dic[i]['property_id'] + """ ?""" + self.dic[i]['name'] + """."""
                    for key, value in self.dic[i]["property_name_dic"].items():
                        rdf_triple += """OPTIONAL{ """ + """?statement""" + str(self.dic[i]['verbose_count']) + """ pq:""" + str(key) + """ ?""" + self.dic[i]['name'] + """_""" + value + """.} """
                else:
                    rdf_triple += """?""" + self.dic[i]["focus"] + """ p:""" + self.dic[i]['property_id'] + """ ?statement""" + str(self.dic[i]['verbose_count']) + """.""" + \
                                  """?statement""" + str(self.dic[i]['verbose_count']) + """ ps:""" + self.dic[i]['property_id'] + """ ?""" + self.dic[i]['name'] + """."""
                    for key, value in self.dic[i]["property_name_dic"].items():
                        rdf_triple += """OPTIONAL{ """ + """?statement""" + str(self.dic[i]['verbose_count']) + """ pq:""" + str(key) + """ ?""" + self.dic[i]['name'] + """_""" + value + """.} """

            # none-verbose version
            else:
                if self.dic[i]["focus"] == "Entity ID":
                    if self.dic[i]["isSubject"]:
                        rdf_triple += """?""" + self.dic[i]["name"] + """ wdt:""" + self.dic[i]["property_id"] + """ wd:""" + self.entity_id + """ ."""
                    else:
                        rdf_triple += """wd:""" + self.entity_id + """ wdt:""" + self.dic[i]["property_id"] + """ ?""" + self.dic[i]["name"] + """ ."""
                else:
                    if self.dic[i]["isSubject"]:
                        rdf_triple += """?""" + self.dic[i]["name"] + """ wdt:""" + self.dic[i]["property_id"] + """ ?""" + self.dic[i]["focus"] + """ ."""
                    else:
                        rdf_triple += """?""" + self.dic[i]["focus"] + """ wdt:""" + self.dic[i]["property_id"] + """ ?""" + self.dic[i]["name"] + """ ."""

        if self.time_property is not None:
            time_filter = """?""" + self.dic[1]["name"] + """ p:""" + self.time_property + """ ?pubdateStatement.
                          ?pubdateStatement ps:""" + self.time_property + """ ?date
                          FILTER (YEAR(?date) = """ + self.time + """)"""

        if self.limit is not None:
            limit_statement = """LIMIT """ + str(self.limit)

        label_statement = """Service wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" }"""

        query = """SELECT DISTINCT """
        for i in range(1, self.count+1):
            if self.dic[i]["rowVerbose"] or self.dic[i]["colVerbose"]:
                query += """?""" + self.dic[i]["name"]
                for key, value in self.dic[i]["property_name_dic"].items():
                    query += """ ?""" + self.dic[i]["name"] + """_""" + value
            else:
                query += """?""" + self.dic[i]["name"] + """ """
        query += """ WHERE {""" + rdf_triple + time_filter + label_statement + """} """ + limit_statement

        return query

    def search_property_for_verbose(self, vbcount):
        property_to_name = {}
        rdf_triple, time_filter, limit_statement = """""", """""", """"""
        for i in range(1, self.count + 1):
            if self.dic[i]["rowVerbose"] or self.dic[i]["colVerbose"]:
                if self.dic[i]["focus"] == "Entity ID":
                    rdf_triple += """wd:""" + self.entity_id + """ p:""" + self.dic[i]['property_id'] + """ ?statement""" + str(self.dic[i]['verbose_count']) + """.""" + \
                                  """?statement""" + str(self.dic[i]['verbose_count']) + """ ps:""" + self.dic[i]['property_id'] + """ ?""" + self.dic[i]['name'] + """.""" \
                                  """?statement""" + str(self.dic[i]['verbose_count']) + """ ?pq""" + str(self.dic[i]['verbose_count']) + """?obj""" + str(self.dic[i]['verbose_count']) + """.""" \
                                  """?qual""" + str(self.dic[i]['verbose_count']) + """ wikibase:qualifier ?pq""" + str(self.dic[i]['verbose_count']) + """."""
                else:
                    rdf_triple += """?""" + self.dic[i]["focus"] + """ p:""" + self.dic[i]['property_id'] + """ ?statement""" + str(self.dic[i]['verbose_count']) + """.""" + \
                                  """?statement""" + str(self.dic[i]['verbose_count']) + """ ps:""" + self.dic[i]['property_id'] + """ ?""" + self.dic[i]['name'] + """.""" \
                                  """?statement""" + str(self.dic[i]['verbose_count']) + """ ?pq""" + str(self.dic[i]['verbose_count']) + """?obj""" + str(self.dic[i]['verbose_count']) + """.""" \
                                  """?qual""" + str(self.dic[i]['verbose_count']) + """ wikibase:qualifier ?pq""" + str(self.dic[i]['verbose_count']) + """."""
            # none-verbose version
            else:
                if self.dic[i]["focus"] == "Entity ID":
                    if self.dic[i]["isSubject"]:
                        rdf_triple += """?""" + self.dic[i]["name"] + """ wdt:""" + self.dic[i][
                            "property_id"] + """ wd:""" + self.entity_id + """ ."""
                    else:
                        rdf_triple += """wd:""" + self.entity_id + """ wdt:""" + self.dic[i]["property_id"] + """ ?""" + \
                                      self.dic[i]["name"] + """ ."""
                else:
                    if self.dic[i]["isSubject"]:
                        rdf_triple += """?""" + self.dic[i]["name"] + """ wdt:""" + self.dic[i][
                            "property_id"] + """ ?""" + self.dic[i]["focus"] + """ ."""
                    else:
                        rdf_triple += """?""" + self.dic[i]["focus"] + """ wdt:""" + self.dic[i][
                            "property_id"] + """ ?""" + self.dic[i]["name"] + """ ."""

        if self.time_property is not None:
            time_filter = """?""" + self.dic[1]["name"] + """ p:""" + self.time_property + """ ?pubdateStatement.
                                  ?pubdateStatement ps:""" + self.time_property + """ ?date
                                  FILTER (YEAR(?date) = """ + self.time + """)"""

        if self.limit is not None:
            limit_statement = """LIMIT """ + str(self.limit)

        label_statement = """Service wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" }"""

        query = """SELECT DISTINCT """
        for i in range(1, self.count + 1):
            if self.dic[i]["rowVerbose"] or self.dic[i]["colVerbose"]:
                query += """ ?qual""" + str(self.dic[i]["verbose_count"]) + """ ?qual""" + str(self.dic[i]["verbose_count"]) + """Label"""
            else:
                query += """?""" + self.dic[i]["name"] + """ """
        query += """ WHERE {""" + rdf_triple + time_filter + label_statement + """} """ + limit_statement
        query_result = get_results(endpoint_url, query)
        for result in query_result['results']['bindings']:
            property_to_name[result['qual' + str(vbcount)]['value'].split('/')[-1]] = result['qual' + str(vbcount) +'Label']['value'].replace(' ', '_')
        return property_to_name

    def generate_trace(self):
        temp_dict = {}
        temp_dict["column name"] = []
        temp_dict["derived from"] = []
        temp_dict["property"] = []
        temp_dict["Subject"] = []
        for i in range(1, self.count + 1):
            temp_dict["column name"].append(self.dic[i]["name"])
            temp_dict["derived from"].append(self.dic[i]["focus"])
            temp_dict["property"].append(self.dic[i]["property_id"])
            temp_dict["Subject"].append(self.dic[i]["isSubject"])
        self.trace = pd.DataFrame(temp_dict)

    def __str__(self):
        return str(self.df)

    def __getattr__(self, col_name):
        if col_name in self.df.columns:
            return self.df[col_name]
        else:
            print(col_name + " has not been found.")
            return None


def createRelation(entity_id: str, property_id=None, isSubject=None, limit=None, rowVerbose=None, colVerbose=None, time_property=None, time=None, name=None):
    if property_id and not name:
        print("Please specify the name of the first column")
        return None
    return Relation(entity_id, property_id, isSubject, limit, rowVerbose, colVerbose, time_property, time, name)

def direct_query(entity_id: str, property_id: str, limit = None, subproperty_id = None):
    result_dict = {}
    rdf_triple, limit_statement = """""", """"""
    label_statement = """Service wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" }"""
    if subproperty_id:
        rdf_triple += """wd:""" + entity_id + """ p:""" + property_id + """ ?dummy .""" + \
                      """?dummy """ + """ps:""" + property_id + """ ?""" + item + """; """ + """pq:""" + subproperty_id + """ ?""" + item + """_1 ."""
    else:
        rdf_triple = """wd:""" + entity_id + """ wdt:""" + property_id + """ ?""" + item + """ ."""

    query = """SELECT DISTINCT ?""" + item + """ """
    if limit is not None:
        limit_statement = """LIMIT """ + str(limit)
    if subproperty_id:
        query += """?""" + item + "_1"
    query += """ WHERE {""" + rdf_triple + label_statement + """} """ + limit_statement

    print(query)
    results = get_results(endpoint_url, query)
    result_dict[get_name(entity_id)] = []
    for result in results["results"]["bindings"]:
        if subproperty_id:
            result_dict[get_name(entity_id)].append((result[item]["value"], result[item + "_1"]["value"]))
        else:
            result_dict[get_name(entity_id)].append(result[item]["value"])
    return result_dict

def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

def define_query(temp_id: str, contain_property:str, isSubject: bool, limit, time_property: str, time:str):

    rdf_triple, time_filter, limit_statement = """""", """""", """"""

    if (isSubject):
        rdf_triple = """?""" + item + """ wdt:""" + contain_property + """ wd:""" + temp_id + """ ."""
    else:
        rdf_triple = """wd:""" + temp_id + """ wdt:""" + contain_property + """ ?""" + item + """ ."""

    if time_property is not None:
        time_filter = """?""" + item + """ p:""" + time_property + """ ?pubdateStatement.
                      ?pubdateStatement ps:""" + time_property + """ ?date
                      FILTER (YEAR(?date) = """ + time + """)"""

    if limit is not None:
        limit_statement = """LIMIT """ + str(limit)

    label_statement = """Service wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" }"""

    query = """SELECT DISTINCT ?""" + item + """ WHERE {""" + rdf_triple + time_filter + label_statement + """} """ + limit_statement

    return query

def get_examples(temp_id: str, contain_property:str, isSubject : bool, limit, time_property: str, time:str):
    result_dict = {temp_id : []}
    query = define_query(temp_id, contain_property, isSubject, limit, time_property, time)
    results = get_results(endpoint_url, query)
    print(results)
    for result in results["results"]["bindings"]:
        result_dict[temp_id].append(result[item]["value"])
    return result_dict

def extend(result_dict: {str: list}, refer_id: str, property_id:str, isSubject : bool,
           limit, time_property: str, time:str):
    result_dict[property_id] = []
    for content in result_dict[refer_id]:
        # print(content)
        content = remove_prefix(content, "http://www.wikidata.org/entity/")
        query = define_query(content, property_id, isSubject, limit, time_property, time)
        # print(query)
        results = get_results(endpoint_url, query)
        # print(results)
        for result in results["results"]["bindings"]:
            # print(content)
            # print(result)
            # print(result)
            result_dict[property_id].append(result[item]["value"])
    return result_dict

def get_name(id: str):
    query = """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
                PREFIX wd: <http://www.wikidata.org/entity/> 
                select  *
                where {
                wd:""" + id + """ rdfs:label ?label .
                FILTER (langMatches( lang(?label), "EN" ) )
                } 
                LIMIT 1"""
    results = get_results(endpoint_url, query)
    result = ''
    for res in results["results"]["bindings"]:
        result = res['label']['value']
    return result

class filters_for_dict:
    entity_list = []
    comparison_list = []
    value_list = []
    number_comparison_list = []
    def add_filter(self, entity, comparison, value, number_comparison):
        self.entity_list.append(entity)
        self.comparison_list.append(comparison)
        self.value_list.append(value)
        self.number_comparison_list.append(number_comparison)

    def filter(self, dict: {str, list}):
        zip_list = zip(self.entity_list, self.comparison_list, self.value_list, self.number_comparison_list)
        for (entity, comparsion, value, number_comparsion) in zip_list:
            # print(entity)
            # print(comparsion)
            # print(value)
            # print(number_comparsion)
            length = len(dict[entity])
            # print(length)
            list_to_delete = []
            i = 0
            while i < length:
                # print(i)
                if number_comparsion:
                    if (comparsion is '=' and int(dict[entity][i]) != int(value)) | (
                            comparsion is '>' and int(dict[entity][i]) <= int(value)) \
                            | (comparsion is '<' and int(dict[entity][i]) >= int(value)) | (
                            comparsion is '!=' and int(dict[entity][i]) == int(value)) \
                            | (comparsion is '>=' and int(dict[entity][i]) < int(value)) | (
                            comparsion is '<=' and int(dict[entity][i]) > int(value)):
                        # if (comparsion is '>' and dict[entity][i] <= value):
                        # print(dict[entity][i])
                        list_to_delete.append(i)
                else:
                    if (comparsion is '=' and dict[entity][i] != value) | (
                            comparsion is '>' and dict[entity][i] <= value) \
                            | (comparsion is '<' and dict[entity][i] >= value) | (
                            comparsion is '!=' and dict[entity][i] == value) \
                            | (comparsion is '>=' and dict[entity][i] < value) | (
                            comparsion is '<=' and dict[entity][i] > value):
                        # if (comparsion is '>' and dict[entity][i] <= value):
                        # print(dict[entity][i])
                        list_to_delete.append(i)
                i += 1
            list_to_delete.sort(reverse=True)
            # print(list_to_delete)
            for index in list_to_delete:
                for key, current_list in dict.items():
                    current_list.pop(index)

# TODO: This class has not yet been used/ implemented completely
class filters_for_query:
    # entity_list = []
    comparison_list = []
    value_list = []

    def add_filter(self, comparison, value):
        # self.enetity_list.append(entity)
        self.comparison_list.append(comparison)
        self.value_list.append(value)

    # This is the version that reserves other content, more like a traditional join
def merge_dict(join_id: str, dict1: {str: list}, dict2: {str: list}):
    if (join_id not in dict1) | (join_id not in dict2):
        print("At least one of the dictionary doesn't contain the key to join")
        return None
    length_dict1 = len(dict1[join_id])
    length_dict2 = len(dict2[join_id])
    dict_merged = {}

    for key, content in dict1.items():
        dict_merged[key] = []
    for key, content in dict2.items():
        dict_merged[key] = []

    for i in range(length_dict1):
        for j in range(length_dict2):
            if (dict1[join_id][i] == dict2[join_id][j]):
                # print('!!')
                for key, content in dict1.items():
                    if (key != join_id):
                        dict_merged[key].append(dict1[key][i])
                for key, content in dict2.items():
                    if (key != join_id):
                        # print(j)
                        dict_merged[key].append(dict2[key][j])
                dict_merged[join_id].append(dict1[join_id][i])
    return dict_merged

# This is the version that does Not reserve the content other than the join_id content, more like an intersection
def intersect_dict(join_id: str, dict1: {str: list}, dict2: {str: list}):
    if (join_id not in dict1) | (join_id not in dict2):
        print("At least one of the dictionary doesn't contain the key to join")
        return None
    length_dict1 = len(dict1[join_id])
    length_dict2 = len(dict2[join_id])
    dict_merged = {join_id: []}
    for i in range(length_dict1):
        for j in range(length_dict2):
            if (dict1[join_id][i] == dict2[join_id][j]):
                dict_merged[join_id].append(dict1[join_id][i])
    return dict_merged


if __name__ == '__main__':
    print("European Union")
    r = createRelation("Q458")
    r.extend("P150", False, "Countries")
    print(r.query_str)
    r.changeFocus("Countries")
    r.extend("P2131", False, "GDP")
    print(r.query_str)
    r.extend("P36", False, "Capitals")
    print(r.query_str)
    r.changeFocus("Capitals")
    r.extend("P1082", False, "Population_of_capitals")
    print(r.query_str)
    r.query()
    print(r)
    print("Capitals")
    print(r.Capitals)

    # print("Obama")
    # r = createRelation("Q76")
    # r.extend("P26", False, "Spouse")
    # print(r.query_str)
    # r.extend("P19", False, "Place_of_birth_president")
    # print(r.query_str)
    # r.changeFocus("Spouse")
    # r.extend("P19", False, "Place_of_birth_spouse")
    # print(r.query_str)
    # r.changeFocus("Place_of_birth_spouse")
    # r.extend("P6", False, "Head_of_government", rowVerbose=True, colVerbose=True)
    # print(r.query_str)
    # r.query()
    # #pd.set_option('display.max_columns', None)
    # print()
    # print("Result:")
    # print(r)
    # print()
    # print("Trace information:")
    # print(r.trace)

    # print()
    # print("Douglas Adams")
    # r = createRelation("Q42")
    # r.extend("P69", False, "Education", rowVerbose=True, colVerbose=True)
    # print(r.query_str)
    # r.changeFocus("Education")
    # r.extend("P17", False, "country", rowVerbose=True, colVerbose=True)
    # print(r.query_str)
    # #r.query()
    # print()
    # print("Result:")
    # print(r)
    # print()
    # print("Trace information:")
    # print(r.trace)

    print()
    print("capital")
    r = createRelation("Q30")
    r.extend("P36", False, "Capital", rowVerbose=True, colVerbose=True)
    print(r.query_str)
    r.changeFocus("Capital")
    r.extend("P1082", False, "Population", rowVerbose=True, colVerbose=True)
    print(r.query_str)
    r.query()
    print()
    print("Result:")
    print(r)
    print()
    print("Trace information:")
    print(r.trace)

