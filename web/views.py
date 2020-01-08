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

    if request.method == 'POST':
        g.user_code = request.form['user_code']

        try:
            g.action, params = check_and_split_user_code(g.user_code)
        except:
            return "Invalid user code!"

        IDs, KP, g.method, refinements, parameter_transformers, g.mappings, KG_table = compiler.kgpcompile(g.action, params, web=True)

        # Computue quality
        g.evaluation_results, total_valid_constraint_count, total_invalid_constraint_count = compiler.compute_quality_metrics(g.action, IDs, KP, g.method, refinements, parameter_transformers, g.mappings, KG_table)

        user_facing_result = compiler.execute_compiled_program(g.mappings, KG_table, parameter_transformers, g.method)
        
        kpid = du.insert(du.INSERT_KP_QUERY, (g.user_code, )).lastrowid

        # TODO multiple results
        if g.method.output_type == "image":
            buf = io.BytesIO()
            user_facing_result.savefig(buf, format='png')
            buf.seek(0)
            blob = buf.read()
            buf.close()
            query = du.INSERT_RESULT_QUERY.format('result_img')
            rid = du.insert(query, (kpid, str(g.method), "WikiData", "KNP_v0", blob, 0, 'image')).lastrowid
        else:
            raise ValueError("not implemented!")

        # defualt shows the first result in the list
        return redirect(url_for("compiler_result", kpid=kpid))
    else:
        ### GET request
        return render_template('compiler_index.html')


@app.route('/compiler/<int:kpid>', methods=['GET'])
@app.route('/compiler/<int:kpid>/rid<int:rid>', methods=['GET'])
@app.route('/compiler/<int:kpid>/rank<int:rank>', methods=['GET'])
def compiler_result(kpid, rid=None, rank=None):

    
    ### Get rid(s) for the kpid
    results = du.query_db("SELECT * from results where kpid=? ORDER BY rank", (kpid, ))
    for result in results:
        # print("keys")
        # print(result.keys())
        type = result['type']
        if type == 'image':
            du.writeTofile(result['result_img'], "web/static/tmp/{}".format(result['rid']))
    
    # defualt shows the first result in the list
    if rid is None and rank is None:
        rid = results[0]['rid']
    if rank:
        rid = results[rank]['rid']

    return render_template('compiler_result.html', results=results, rid=rid, mappings=g.mappings, evaluation_results=g.evaluation_results, user_code=g.user_code, method=g.method, action=g.action)



def check_and_split_user_code(user_code):

    left_p = user_code.find("(")
    right_p = user_code.find(")")
    action = user_code[0:left_p]
    params = user_code[left_p + 1: right_p].split("|")
    return (action, params)