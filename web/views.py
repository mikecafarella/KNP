from flask import Flask, redirect, url_for, render_template, request, current_app, g, abort
from refinements import RefinementConstraint
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
import methods
import refinements
import os

@app.route('/compiler', methods=['GET', 'POST'])
def compiler_index(user_code=None, kpid=None, rank=0):
    """Homepage of the compiler. The arguments are not None only when re-executing a kp."""

    if request.method == 'POST' or user_code:

        if not user_code:
            user_code = request.form['user_code']

        try:
            action, params = check_and_split_user_code(user_code)
        except:
            return "Invalid user code!"

        IDs, KP, method, refinements, parameter_transformers, mappings, KG_table = compiler.kgpcompile(action, params, web=True)

        # for added constraints
        # if modified_refinements:
        #     refinements = modified_refinements

        # Computue quality
        evaluation_results, total_valid_constraint_count, total_invalid_constraint_count = compiler.compute_quality_metrics(action, IDs, KP, method, refinements, parameter_transformers, mappings, KG_table)

        if not total_invalid_constraint_count:
            # all constraints are satisfied
            user_facing_result = compiler.execute_compiled_program(mappings, KG_table, parameter_transformers, method)
            kpid = du.insert_successful_results(user_code, action, params, IDs, method, refinements, parameter_transformers, mappings, evaluation_results, user_facing_result, kpid, rank)
        else:
            # There are unsatisfied constraints, don't execute
            kpid = du.insert_failed_results(user_code, action, params, IDs, method, evaluation_results, mappings, kpid, rank)
        
        # print("kpid {}".format(kpid))
        # defualt shows the first result in the list
        return redirect(url_for("compiler_result", kpid=kpid, rank=rank))
    else:
        ### GET request
        return render_template('compiler_index.html')


@app.route('/results/kpid<int:kpid>', methods=['GET'])
@app.route('/results/kpid<int:kpid>/rank<int:rank>', methods=['GET'])
def compiler_result(kpid, rank=None):

    # defualt shows the first result in the list
    if rank is None:
        return redirect(url_for("compiler_result", kpid=kpid, rank=0))

    ### Get entity links
    # print("kpid {}".format(kpid))
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

    refinements_row = du.query_db("SELECT refinement_name, GROUP_CONCAT(constraint_name, ','), GROUP_CONCAT(true_false, ',') FROM constraint_evaluation_results where rid=? GROUP BY refinement_name", (displayed_result['rid'], ))
    refinements = {}

    for refinement in refinements_row:
        constraints = refinement[1].split(",")
        constraints_true_false = refinement[2].split(",")
        refinements[refinement['refinement_name']] = [ (constraints[i], constraints_true_false[i]) for i in range(len(constraints))]


    mapping = json.loads(displayed_result['mapping'])
    try:
        parameter_transformers = json.loads(displayed_result['parameter_transformers'])
    except:
        parameter_transformers = None
    method = utils.get_method_by_name(displayed_result['method_name'])()  # method instance

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


@app.route('/refinement/<string:refinement_name>', methods=['GET'])
def refinement(refinement_name):
    refinement = utils.get_refinement_by_name(refinement_name)
    return render_template("code.html", code=inspect.getsource(refinement), name=refinement_name, type="refinement")


@app.route('/method/<string:method_name>', methods=['GET'])
def method(method_name):
    method = utils.get_method_by_name(method_name)
    return render_template("code.html", code=inspect.getsource(method), name=method_name, type="method")


@app.route('/constraint/<string:constraint_name>', methods=['GET'])
def constraint(constraint_name):
    constraint = utils.get_constraint_by_name(constraint_name)
    return render_template("code.html", code=inspect.getsource(constraint), name=constraint_name, type="constraint")


@app.route("/create", methods=['POST'])
@app.route("/create/<string:type>/", methods=['GET'])
def create(type=None):
    if request.method == 'GET':
        return render_template("create.html", type=type)
    elif request.method == 'POST':
        type = request.form['type']
        name = request.form['name']
        code = request.form['code']

        exec(code, globals())
        if type == 'constraint' or type == 'refinement':
            setattr(refinements, name, globals()[name])
            with open('refinements.py', 'a+') as f:
                f.write("\n\n")
                f.write(code)
        elif type == 'method':
            setattr(methods, name, globals()[name])
        # TODO make the change non-volatile

        return "OK"


@app.route("/add_constraint/kpid<int:kpid>/rank<int:rank>/<string:refinement_name>'", methods=['POST', 'GET'])
def add_constraint(kpid, rank, refinement_name):

    new_constraint_name = request.form['new_constraint_name']
    # add the constraint to the refinement

    # refinement = getattr(refinements, refinement_name)()  # Have to make it an instance
    constraint = getattr(refinements, new_constraint_name)()
    getattr(refinements, refinement_name).add_constraints([constraint])
    # refinement = getattr(refinements, refinement_name)()
    # refinement.constraints.append(constraint)

    # grab the original result from DB
    old_result = du.query_db("SELECT * from results where kpid=? AND rank=?", (kpid, rank), one=True)
    old_kp = du.query_db("SELECT * from knowledge_programs where kpid=?", (kpid, ), one=True)

    # Drop old data in DB
    du.query_db("DELETE from results where rid=?", (old_result['rid'], ))
    du.query_db("DELETE from constraint_evaluation_results where rid=?", (old_result['rid'], ))

    # Re-execute for new result

    # return compiler_index([refinement], user_code=old_kp['user_code'], kpid=kpid, rank=rank)
    return compiler_index(user_code=old_kp['user_code'], kpid=kpid, rank=rank)


def check_and_split_user_code(user_code):
    left_p = user_code.find("(")
    right_p = user_code.find(")")
    action = user_code[0:left_p]
    params = user_code[left_p + 1: right_p].split("|")
    return (action, params)



# Compare(Q30:United States of America.P2131:nominal GDP|Q16:Canada.P2131:nominal GDP)

class Test(RefinementConstraint):
    """This constraint means that all parameters must have the same KG type."""

    @staticmethod
    def test_all_parameters_constraint_on_reference(IDs):
        """Test that all the parameters are named via the same attribute."""
        return len(set(map(lambda x: x[-1], IDs))) == 1