from flask import Flask, redirect, url_for, render_template, request, current_app, g, abort
import sys
from web import app
import wikidata_utils as wu
import compiler
import web.db_utils as du
import json
import utils
import inspect
import iso8601
import pandas as pd

@app.route('/compiler', methods=['GET', 'POST'])
def compiler_index():
    """Homepage of the compiler."""

    if request.method == 'POST':
        user_code = request.form['user_code']

        try:
            action, params = check_and_split_user_code(user_code)
        except:
            return "Invalid user code!"

        IDs, KP, method, refinements, parameter_transformers, mappings, KG_table = compiler.kgpcompile(action, params, web=True)

        # Computue quality
        evaluation_results, total_valid_constraint_count, total_invalid_constraint_count = compiler.compute_quality_metrics(action, IDs, KP, method, refinements, parameter_transformers, mappings, KG_table)

        user_facing_result = compiler.execute_compiled_program(mappings, KG_table, parameter_transformers, method)
        
        kpid = du.insert_results(user_code, action, params, IDs, method, refinements, parameter_transformers, mappings, evaluation_results, user_facing_result)

        # defualt shows the first result in the list
        return redirect(url_for("compiler_result", kpid=kpid, rank=0))
    else:
        ### GET request
        return render_template('compiler_index.html')


@app.route('/results/kpid<int:kpid>', methods=['GET'])
@app.route('/results/kpid<int:kpid>/rank<int:rank>', methods=['GET'])
def compiler_result(kpid, rid=None, rank=None):

    # defualt shows the first result in the list
    if rank is None:
        return redirect(url_for("compiler_result", kpid=kpid, rank=0))

    ### Get entity links
    kp = du.query_db("SELECT * from knowledge_programs where kpid=?", (kpid, ), one=True)
    user_code = kp['user_code']
    KG_params = json.loads(kp['KG_params'])
    # KG_params = [[param_text, entity_page_link, json_data_link], ...]
    KG_params_links = []
    for KG_param in KG_params:
        KG_params_links.append((KG_param, wu.get_entity_link(KG_param), wu.get_json_link(KG_param)))


    ### Get rid(s) for the kpid
    results = du.query_db("SELECT * from results where kpid=? ORDER BY rank", (kpid, ))

    for result in results:
        type = result['type']
        if type == 'image':
            du.writeTofile(result['result_img'], "web/static/tmp/kpid{}rank{}".format(kpid, result['rank']))
    
    displayed_result = results[rank]

    mapping = json.loads(displayed_result['mapping'])
    parameter_transformers = json.loads(displayed_result['parameter_transformers'])
    method = utils.get_method_by_name(displayed_result['method_name'])()  # method instance

    refinements_row = du.query_db("SELECT refinement_name, GROUP_CONCAT(constraint_name, ','), GROUP_CONCAT(true_false, ',') FROM constraint_evaluation_results where rid=? GROUP BY refinement_name", (displayed_result['rid'], ))
    refinements = {}

    for refinement in refinements_row:
        constraints = refinement[1].split(",")
        constraints_true_false = refinement[2].split(",")
        refinements[refinement['refinement_name']] = [ (constraints[i], constraints_true_false[i]) for i in range(len(constraints))]
    
    return render_template('compiler_result.html', kpid=kpid, rank=rank, method=method, refinements=refinements, user_code=user_code, mapping=mapping, KG_params_links=KG_params_links, results=results, parameter_transformers=parameter_transformers)


@app.route('/KG_data/<string:KG_param>', methods=['GET'])
@app.route('/KG_data/<string:KG_param>/<string:column>', methods=['GET'])
def KG_data(KG_param, column=None):

    head = KG_param
    if column:
        head += "['{}']".format(column)

    KG_param = KG_param.split(".")
    KG_param = [x[0:x.find(":")] for x in KG_param]
    KG_data = utils.get_KG_data((KG_param, ))[0]
    if KG_data['type'] == 'claims':
        KG_data = utils.Dataset(KG_data['data'], KG_param)
    elif KG_data['type'] == 'entity':
        KG_data = utils.Entity(KG_data['data'], KG_param)

    if column:
        return render_template("KG_data.html", data=KG_data[column].to_frame().to_html(), head=head)
    else:
        return render_template("KG_data.html", data=KG_data.data_frame.to_html(), head=head)


@app.route('/method/<string:method_name>', methods=['GET'])
def method(method_name):

    method = utils.get_method_by_name(method_name)
    return render_template("method.html", code=inspect.getsource(method))


@app.route('/transformer/<string:transformer>', methods=['GET'])
def transformer(transformer):
    return transformer


@app.route('/method_data/<string:KG_param>/<string:column>/<string:transformer>', methods=['GET'])
@app.route('/method_data/<string:raw_data>/<string:transformer>', methods=['GET'])
def method_data(transformer, KG_param=None, column=None, raw_data=None):
    if raw_data:
        return eval(transformer)(raw_data)
    else:
        KG_param = KG_param.split(".")
        KG_param = [x[0:x.find(":")] for x in KG_param]
        KG_data = utils.get_KG_data((KG_param, ))[0]
        if KG_data['type'] == 'claims':
            KG_data = utils.Dataset(KG_data['data'], KG_param)
        elif KG_data['type'] == 'entity':
            KG_data = utils.Entity(KG_data['data'], KG_param)

        return pd.DataFrame(eval(transformer)(KG_data[column])).to_html()


def check_and_split_user_code(user_code):
    left_p = user_code.find("(")
    right_p = user_code.find(")")
    action = user_code[0:left_p]
    params = user_code[left_p + 1: right_p].split("|")
    return (action, params)



# Compare(Q30:United States of America.P2131:nominal GDP|Q16:Canada.P2131:nominal GDP)