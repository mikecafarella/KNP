# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

import sys
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"
item = "item"

class Result:
    """
    The class returned when get/extend is called.
    It contains string field with query.
    We call Result.query when we need to do the query.
    """
    def __init__(self, temp_id: str, property_id: str, isSubject: bool, limit, time_property: str, time: str):
        self.temp_id = temp_id
        self.property_id = property_id
        self.isSubject = isSubject
        self.limit = limit
        self.time_property = time_property
        self.time = time
        self.query_str = define_query(temp_id, property_id, isSubject, limit, time_property, time)
        self.dic = {}
        self.result_dic = {}
        self.count = 0

    def query(self):
        #self.query_str = self.define_query_for_result()
        results = get_results(endpoint_url, self.query_str)
        result_dict = {}
        result_dict[get_name(self.temp_id)] = []
        for i in range(1, self.count + 1):
            result_dict[get_name(self.dic[i]["property_id"])] = []
        for result in results['results']['bindings']:
            for key, value in result.items():
                if key == item:
                    result_dict[get_name(self.temp_id)].append(value['value'])
                else:
                    result_dict[get_name(self.dic[int(key[-1])]["property_id"])].append(value['value'])
        self.result_dic = result_dict
        return result_dict

    def extend(self, refer_id: str, property_id: str, isSubject: bool, time_property: str, time: str):
        self.count += 1
        self.dic[self.count] = {}
        self.dic[self.count]["property_id"] = property_id
        self.dic[self.count]["isSubject"] = isSubject
        self.dic[self.count]['time_property'] = time_property
        self.dic[self.count]['time'] = time
        self.query_str = self.define_query_for_result()

    def entend_all(self, refer_id: str, property_id: str, isSubject: bool, time_property: str, time: str, subproperty_id):
        # This is for getting population list (history)
        # isSubject must be false
        self.count += 1
        self.dic[self.count] = {}
        self.dic[self.count]["property_id"] = property_id
        self.dic[self.count]["subproperty_id"] = subproperty_id
        self.dic[self.count]["isSubject"] = isSubject
        self.dic[self.count]['time_property'] = time_property
        self.dic[self.count]['time'] = time
        self.query_str = self.define_query_for_all_result()

    def define_query_for_result(self):

        rdf_triple, time_filter, limit_statement = """""", """""", """"""

        if (self.isSubject):
            rdf_triple = """?""" + item + """ wdt:""" + self.property_id + """ wd:""" + self.temp_id + """ ."""
        else:
            rdf_triple = """wd:""" + self.temp_id + """ wdt:""" + self.property_id + """ ?""" + item + """ ."""

        if (self.dic[1]['isSubject']):
            rdf_triple += """?""" + item + str(1) + """ wdt:""" + self.dic[1]['property_id'] + """ ?""" + item + """ ."""
        else:
            rdf_triple += """?""" + item + """ wdt:""" + self.dic[1]['property_id'] + """ ?""" + item + str(1) + """ ."""

        if self.count >= 2:
            for i in range(2, self.count + 1):
                if (self.dic[i]['isSubject']):
                    rdf_triple += """?""" + item + str(i) + """ wdt:""" + self.dic[i]['property_id'] + """ ?""" + item + str(i-1) + """ ."""
                else:
                    rdf_triple += """?""" + item + str(i-1) + """ wdt:""" + self.dic[i]['property_id'] + """ ?""" + item + str(i) + """ ."""

        if self.time_property is not None:
            time_filter = """?""" + item + """ p:""" + self.time_property + """ ?pubdateStatement.
                          ?pubdateStatement ps:""" + self.time_property + """ ?date
                          FILTER (YEAR(?date) = """ + self.time + """)"""

        if self.limit is not None:
            limit_statement = """LIMIT """ + str(self.limit)

        label_statement = """Service wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" }"""

        query = """SELECT DISTINCT ?""" + item + """ """
        if self.count >= 1:
            for i in range(1, self.count+1):
                query += """?""" + item + str(i) + """ """
        query += """ WHERE {""" + rdf_triple + time_filter + label_statement + """} """ + limit_statement

        return query

    def define_query_for_all_result(self):
        # isSubject must be false

        rdf_triple, time_filter, limit_statement = """""", """""", """"""

        if (self.isSubject):
            rdf_triple = """?""" + item + """ wdt:""" + self.property_id + """ wd:""" + self.temp_id + """ ."""
        else:
            rdf_triple = """wd:""" + self.temp_id + """ wdt:""" + self.property_id + """ ?""" + item + """ ."""

        if (self.dic[1]['isSubject']):
            rdf_triple += """?""" + item + str(1) + """ wdt:""" + self.dic[1]['property_id'] + """ ?""" + item + """ ."""
        else:
            rdf_triple += """?""" + item + """ wdt:""" + self.dic[1]['property_id'] + """ ?""" + item + str(1) + """ ."""

        if self.count >= 2:
            for i in range(2, self.count):
                if (self.dic[i]['isSubject']):
                    rdf_triple += """?""" + item + str(i) + """ wdt:""" + self.dic[i]['property_id'] + """ ?""" + item + str(i-1) + """ ."""
                else:
                    rdf_triple += """?""" + item + str(i-1) + """ wdt:""" + self.dic[i]['property_id'] + """ ?""" + item + str(i) + """ ."""

            rdf_triple += """?""" + item + str(self.count - 1) + """ p:""" + self.dic[-1]['property_id'] + """ ?dummy .""" +\
                          """?dummy """ + """ps:""" + self.dic[-1]['property_id'] + """ ?""" + item + str(self.count) + """; """ + """pq:""" + self.dic[-1]['subproperty_id'] + """ ?""" + item + str(self.count) + """_1 ."""

        if self.time_property is not None:
            time_filter = """?""" + item + """ p:""" + self.time_property + """ ?pubdateStatement.
                          ?pubdateStatement ps:""" + self.time_property + """ ?date
                          FILTER (YEAR(?date) = """ + self.time + """)"""

        if self.limit is not None:
            limit_statement = """LIMIT """ + str(self.limit)

        label_statement = """Service wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" }"""

        query = """SELECT DISTINCT ?""" + item + """ """
        if self.count >= 1:
            for i in range(1, self.count):
                query += """?""" + item + str(i) + """ """
            query += """?""" + item + str(self.count) + """ ?""" + item + str(self.count) + "_1"
        query += """ WHERE {""" + rdf_triple + time_filter + label_statement + """} """ + limit_statement

        return query

    def __str__(self):
        return self.query_str


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
        self.count = 0
        self.time_property = time_property
        self.time = time
        self.limit = limit
        self.focus = "Entity ID"
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
                result_dict[self.dic[i]["name"]+"_2"] = []
        for result in results['results']['bindings']:
            for key, value in result.items():
                if key[-2] == "_":
                    if key[-1] == "1":
                        result_dict[self.dic[i]["name"]].append(value['value'])
                    else:
                        if self.dic[i]["colVerbose"]:
                            result_dict[self.dic[i]["name"]+"_2"].append(value['value'])
                else:
                    result_dict[key].append(value['value'])
        if self.dic[i]["colVerbose"] and not self.dic[i]["rowVerbose"]:
            idx = result_dict[self.dic[i]["name"]+"_2"].index(max(result_dict[self.dic[i]["name"]+"_2"]))
            result_dict[self.dic[i]["name"]+"_2"] = [max(result_dict[self.dic[i]["name"]+"_2"])]
            result_dict[self.dic[i]["name"]] = [result_dict[self.dic[i]["name"]][idx]]
        result_dict["Entity ID"] = ['http://www.wikidata.org/entity/' + str(self.entity_id)] * len(result_dict[self.dic[self.count]["name"]])
        self.result_dic = result_dict
        return result_dict

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
        if time_property and time:
            self.time_property = time_property
            self.time = time
        if limit:
            self.limit = limit
        self.query_str = self.define_query_relation()

    def changeFocus(self, name = "Entity ID"):
        self.focus = name

    def define_query_relation(self):

        rdf_triple, time_filter, limit_statement = """""", """""", """"""

        if self.count < 1:
            return None

        # TODO: May be some problems regarding verbose
        for i in range(1, self.count + 1):
            if self.dic[i]["rowVerbose"] or self.dic[i]["colVerbose"]:
                if self.dic[i]["focus"] == "Entity ID":
                    rdf_triple += """wd:""" + self.entity_id + """ p:""" + self.dic[i]['property_id'] + """ ?statement.""" + \
                                """?statement """ + """ps:""" + self.dic[i]['property_id'] + """ ?""" + self.dic[i]['name'] + """_1.""" + \
                                """?statement """ + """?pq """ + """?""" + self.dic[i]['name'] + """_2.""" + \
                                """?qual wikibase:qualifier ?pq."""
                else:
                    rdf_triple += """?""" + self.dic[i]["focus"] + """ p:""" + self.dic[i]['property_id'] + """ ?statement.""" + \
                                  """?statement """ + """ps:""" + self.dic[i]['property_id'] + """ ?""" + self.dic[i]['name'] + """_1.""" + \
                                  """?statement """ + """?pq """ + """?""" + self.dic[i]['name'] + """_2.""" + \
                                  """?qual wikibase:qualifier ?pq."""
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
                query += """?""" + self.dic[i]["name"] + """_1 ?""" + self.dic[i]["name"] + """_2 """
            else:
                query += """?""" + self.dic[i]["name"] + """ """
        query += """ WHERE {""" + rdf_triple + time_filter + label_statement + """} """ + limit_statement

        return query

    def __str__(self):
        string = "{\n"
        flag = True
        for key, value in self.result_dic.items():
            if flag:
                string += key + ": " + str(value)
                flag = False
            else:
                string += ",\n" + key + ": " + str(value)
        string += "\n}"
        return string

    def __getattr__(self, col_name):
        if col_name in self.result_dic.keys():
            return self.result_dic[col_name]
        else:
            print(col_name + " has not been found.")
            return None


def createRelation(entity_id: str, property_id=None, isSubject=None, limit=None, rowVerbose=None, colVerbose=None, time_property=None, time=None, name=None):
    if property_id and not name:
        print("Please specify the name of the first column")
        return None
    return Relation(entity_id, property_id, isSubject, limit, rowVerbose, colVerbose, time_property, time, name)

def get_examples_new(temp_id: str, contain_property:str, isSubject : bool, limit, time_property: str, time:str):
    results = Result(temp_id, contain_property, isSubject, limit, time_property, time)
    return results

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
    print("USA population history")
    r = createRelation("Q30")
    r.extend("P1082", isSubject=False, isVerbose=True)
    print(r)
    r.query()
    print(r.result_dic)

    print()
    print("Latest population of Canada")
    r = createRelation("Q16", "P1082", isSubject=False)
    print(r)
    r.query()
    print(r.result_dic)

    print()
    print("Population of the capital city of every country in the European Union")
    r = createRelation("Q458", "P150", isSubject=False)
    print(r)
    r.extend("P36", isSubject=False)
    print(r)
    r.extend("P1082", isSubject=False, isVerbose=True)
    print(r)
    r.query()
    print(r.result_dic)

    print()
    print("Film Actor")
    r = createRelation("Q10800557", "P106", isSubject=True, limit=10)
    print(r)
    r.extend("P19", isSubject=False)
    print(r)
    r.extend("P1082", isSubject=False)
    print(r)
    r.query()
    print(r.result_dic)

    print("USA population history")
    print("Multiple rows")
    r = createRelation("Q30")
    r.extend("P1082", isSubject=False, rowVerbose=True)
    r.query()
    print(r.result_dic)

    print("Multiple columns")
    r = createRelation("Q30")
    r.extend("P1082", isSubject=False, colVerbose=True)
    r.query()
    print(r.result_dic)

    print("Verbose")
    r = createRelation("Q30")
    r.extend("P1082", isSubject=False, rowVerbose=True, colVerbose=True)
    r.query()
    print(r.result_dic)

    print("Non-verbose")
    r = createRelation("Q30")
    r.extend("P1082", isSubject=False)
    r.query()
    print(r.result_dic)

    print()
    print("Examples of books published in 1998")
    r = createRelation("Q571", "P31", isSubject=True, limit=10, time="1998", time_property="P577")
    print(r)
    r.query()
    print(r.result_dic)




    print("USA population history")
    result = direct_query("Q30", "P1082", None, "P585")
    print(result)

    print()
    print("Latest population of Canada")
    result = direct_query("Q16", "P1082")
    print(result)

    print()
    print("GDP of every country in the European Union")
    result = get_examples_new("Q458", "P150", False, None, None, None)
    print(result)
    result.extend("Q458", "P2131", False, None, None)
    print(result)
    print(result.query())

    print()
    print("Examples of books published in 1998")
    result = get_examples_new("Q571", "P31", True, 10, "P577", "1998")
    print(result)
    print(result.query())


    print()
    print("Film Actor")
    result = get_examples_new("Q10800557", "P106", True, 10, None, None)
    print(result)
    result.extend("Q10800557", "P19", False, None, None)
    print(result)
    result.extend("P19", "P1082", False, None, None)
    print(result)
    print(result.query())

    print(get_name("Q10800557"))

    print("new_dict_filter:")
    new_dict_filter = filters_for_dict()
    new_dict_filter.add_filter('P1082', '>', 38115, True)
    print(new_dict_filter.entity_list)
    print(new_dict_filter.comparison_list)
    print(new_dict_filter.value_list)
    new_dict_filter.filter(result)
    print(result)


    print('Test merge & intersection')
    dict1 = {'Q1': ['1', '2', '4', '8'], 'Q2': ['100', '200', '300', '400']}
    dict2 = {'Q1': ['2', '4', '6', '8'], 'Q3': ['-100', '-200', '-300', '-400']}
    print(merge_dict('Q1', dict1, dict2))
    print(intersect_dict('Q1', dict1, dict2))

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

    print()
    print("Obama")
    r = createRelation("Q76")
    r.extend("P26", False, "Spouse")
    print(r.query_str)
    r.extend("P19", False, "Place_of_birth_president")
    print(r.query_str)
    r.changeFocus("Spouse")
    r.extend("P19", False, "Place_of_birth_spouse")
    print(r.query_str)
    r.changeFocus("Place_of_birth_spouse")
    r.extend("P1082", False, "population", rowVerbose=True, colVerbose=True)
    print(r.query_str)
    r.query()
    print(r)
    print(r.Place_of_birth_spouse)

    print()
    print("President")
    r = createRelation("Q11696")
    r.extend("P39", True, "Presidents")
    r.changeFocus("Presidents")
    r.extend("P26", False, "Spouses")
    r.extend("P569", False, "Date_of_birth_president")
    r.changeFocus("Spouses")
    r.extend("P569", False, "Date_of_birth_spouse")
    r.query()
    print(r)

