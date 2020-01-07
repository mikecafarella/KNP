from flask import Flask, redirect, url_for, render_template, request, current_app, g, abort
import sys
from web import app
import wikidata_utils as wu
import compiler
import web.db_utils as du
import io

@app.route('/compiler', methods=['GET', 'POST'])
def compiler_index():
    """Homepage of the compiler."""

    return render_template('compiler_index.html')
    

@app.route('/compiler/result', methods=['POST'])
def compiler_result():

    user_code = request.form['user_code']
    # IDs = request.form['IDs'] + ")"

    try:
        # _, IDs = check_and_split_user_code(IDs)
        action, params = check_and_split_user_code(user_code)
    except:
        return "Invalid user code!"

    IDs, KP, method, refinements, parameter_transformers, mappings, KG_table = compiler.kgpcompile(action, params, web=True)

    # Computue quality
    evaluation_results, total_valid_constraint_count, total_invalid_constraint_count = compiler.compute_quality_metrics(action, IDs, KP, method, refinements, parameter_transformers, mappings, KG_table)

    user_facing_result = compiler.execute_compiled_program(mappings, KG_table, parameter_transformers, method)
    
    kpid = du.insert(du.INSERT_KP_QUERY, (user_code, )).lastrowid

    # TODO multiple results
    if method.output_type == "image":
        buf = io.BytesIO()
        user_facing_result.savefig(buf, format='png')
        buf.seek(0)
        blob = buf.read()
        buf.close()
        query = du.INSERT_RESULT_QUERY.format('result_img')
        rid = du.insert(query, (kpid, str(method), "WikiData", "KNP_v0", blob, 1)).lastrowid
        du.writeTofile(blob, "web/static/tmp/{}".format(rid))
        
    return render_template('compiler_result.html', rid=rid, mappings=mappings, evaluation_results=evaluation_results, user_code=request.form['user_code'], method=method, action=action)



def check_and_split_user_code(user_code):

    left_p = user_code.find("(")
    right_p = user_code.find(")")
    action = user_code[0:left_p]
    params = user_code[left_p + 1: right_p].split("|")
    # for i in range(len(params)):
    #     params[i] = params[i].split(".")
    #     params[i] = [x[0:x.find(":")] for x in params[i]]
    #     params[i] = ".".join(params[i])
    return (action, params)