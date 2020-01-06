from flask import Flask, redirect, url_for, render_template, request, current_app, g, abort
import yaml
import sys
from web import app
import wikidata_utils as wu
import compiler

@app.route('/compiler', methods=['GET', 'POST'])
def compiler_index():
    """Homepage of the compiler."""
    if request.method == 'GET':
        return render_template('compiler_index.html')
    elif request.method == 'POST':
        user_code = request.form['user_code']
        try:
            action, KG_references = check_and_split_user_code(user_code)
        except:
            return "Invalid user code!"
        
        IDs, KP, method, refinements, parameter_transformers, mapping, KG_table = compiler.kgpcompile(action, KG_references)

        # Computue quality
        evaluation_results, total_valid_constraint_count, total_invalid_constraint_count = compiler.compute_quality_metrics(IDs, KP, method, refinements, parameter_transformers, mapping, KG_table)

        return render_template('compiler_index.html', mapping=mapping, evaluation_results=evaluation_results)


def check_and_split_user_code(user_code):

    left_p = user_code.find("(")
    right_p = user_code.find(")")
    action = user_code[0:left_p]
    params = user_code[left_p + 1: right_p].split("|")
    return (action, params)