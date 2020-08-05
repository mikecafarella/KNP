# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

import sys
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"
item = "item"

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
                      ?pubdateStatement ps:""" + time_property + """?date
                      FILTER (YEAR(?date) = """ + time + """)"""

    if limit is not None:
        limit_statement = """LIMIT """ + str(limit)

    query = """SELECT DISTINCT ?""" + item + """ WHERE {""" + rdf_triple + time_filter + """} """ + limit_statement

    return query

def get_examples(temp_id: str, contain_property:str, isSubject : bool, limit, time_property: str, time:str):
    result_dict = {temp_id : []}
    query = define_query(temp_id, contain_property, isSubject, limit, time_property, time)
    results = get_results(endpoint_url, query)
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

result = get_examples("Q10800557", "P106", True, 10, None, None)
print(result)
result = extend(result, "Q10800557", "P19", False, None, None, None)
print(result)
result = extend(result, "P19", "P1082", False, None, None, None)
print(result)
print(get_name("Q10800557"))

print("new_dict_filter:")
new_dict_filter = filters_for_dict()
new_dict_filter.add_filter('P1082', '>', 38115, True)
print(new_dict_filter.entity_list)
print(new_dict_filter.comparison_list)
print(new_dict_filter.value_list)
new_dict_filter.filter(result)
print(result)

print(int('38115') < int('12500123'))

print('Test merge & intersection')
dict1 = {'Q1': ['1', '2', '4', '8'], 'Q2': ['100', '200', '300', '400']}
dict2 = {'Q1': ['2', '4', '6', '8'], 'Q3': ['-100', '-200', '-300', '-400']}
print(merge_dict('Q1', dict1, dict2))
print(intersect_dict('Q1', dict1, dict2))

