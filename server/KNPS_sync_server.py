from datetime import datetime

import kgpl
import flask
import pickle
import json
# import BulkLoader
# from kgpl import KNPSStore
from sqlalchemy.orm import session
# from kgpl.KNPSStore import Session
# import server

app = flask.Flask(__name__)
# s = KNPSStore(None)
server_store = kgpl.store
APPLICATION_ROOT = '/'


@app.route("/", methods=['GET', 'POST'])
def main():
    curnum = server_store.availVar()
    # if flask.request.method == 'POST':
    #     vnum = flask.request.form['Variable_Name']
    #     # check whether vnum is from 1 to len(s.valueList)
    #
    #     if 1 <= int(vnum) <= curnum:
    #         vname = "V" + str(vnum)
    #         var = s.GetVariable(vname)
    #         his = var.historical_vals
    #         print(his)
    #         print("@@@@@@@@@@@@@@@@@@@@@@", type(his))
    #         pretty_time = []
    #         for onehis in his:
    #             value_value = s.GetValue(onehis[1])
    #             pretty_time.append(
    #                 (datetime.fromtimestamp(onehis[0]).strftime(
    #                     '%Y-%m-%d %H:%M:%S'), onehis[1],
    #                  type(value_value).__name__,
    #                  value_value.val),
    #             )
    #         context = {
    #             "vname": vname,
    #             "var": pretty_time
    #         }
    #         return flask.render_template("result.html", **context)
    #     else:
    #         context = {
    #             "existing_variables": curnum,
    #             "invalid": "Invalid Input! Please retry."
    #         }
    #         return flask.render_template("index.html", **context)

    # else:
    context = {
        "existing_variables": curnum}
    # return flask.jsonify(**context), 200
    # return flask.render_template("index.html", **context)

    return flask.render_template("index.html", **context)


@app.route("/allvars", methods=['GET', 'POST'])
def allvars():
    if flask.request.method == 'POST':
        var_name = flask.request.form['Variable_Name']
        return flask.redirect("/allvars/" + var_name)
    else:
        curnum = server_store.availVar()
        pretty_time = []

        for i in range(1, curnum + 1, 1):
            vname = "V" + str(i)
            var = server_store.GetVariable(vname)
            value_value = server_store.GetValue(var.currentvalue)
            pretty_time.append(
                (datetime.fromtimestamp(var.timestamp).strftime(
                    '%Y-%m-%d %H:%M:%S'),
                 type(value_value).__name__,
                 value_value.val,
                 var.currentvalue,
                 i)
            )
        context = {
            "list_var": pretty_time
        }
    return flask.render_template("all_var.html", **context)


@app.route("/allvars/<varname>", methods=['GET', 'POST'])
def onevar(varname):
    if flask.request.method == 'GET':
        curnum = server_store.availVar()
        vnum = varname
        # check whether vnum is from 1 to len(s.valueList)

        if 1 <= int(vnum) <= curnum:
            vname = "V" + str(vnum)
            var = server_store.GetVariable(vname)
            his = var.historical_vals
            # print(his)
            # print("@@@@@@@@@@@@@@@@@@@@@@", type(his))
            pretty_time = []
            for onehis in his:
                value_value = server_store.GetValue(onehis[1])
                pretty_time.append(
                    (datetime.fromtimestamp(onehis[0]).strftime(
                        '%Y-%m-%d %H:%M:%S'), onehis[1],
                     type(value_value).__name__,
                     value_value.val),
                )
            context = {
                "vnum": vnum,
                "vname": vname,
                "var": pretty_time
            }
            return flask.render_template("result.html", **context)
        else:
            context = {
                "existing_variables": curnum,
                "invalid": "Invalid Input! Please retry."
            }
            return flask.render_template("index.html", **context)
    else:
        # print(kgpl.kgval(flask.request.form['new_val']))
        # kgpl.store.empty_bulk_list()
        var = server_store.GetVariable("V" + str(varname))
        try:
            json_rst = json.loads(flask.request.form['new_val'])
        except json.decoder.JSONDecodeError:
            print("wrong format")
            curnum = server_store.availVar()
            vnum = varname
            # check whether vnum is from 1 to len(s.valueList)

            if 1 <= int(vnum) <= curnum:
                vname = "V" + str(vnum)
                var = server_store.GetVariable(vname)
                his = var.historical_vals
                # print(his)
                # print("@@@@@@@@@@@@@@@@@@@@@@", type(his))
                pretty_time = []
                for onehis in his:
                    value_value = server_store.GetValue(onehis[1])
                    pretty_time.append(
                        (datetime.fromtimestamp(onehis[0]).strftime(
                            '%Y-%m-%d %H:%M:%S'), onehis[1],
                         type(value_value).__name__,
                         value_value.val),
                    )
                context = {
                    "vnum": vnum,
                    "vname": vname,
                    "var": pretty_time,
                    "invalid":"invalid"
                }
                return flask.render_template("result.html", **context)
            else:
                context = {
                    "existing_variables": curnum,
                    "invalid": "Invalid Input! Please retry."
                }
                return flask.render_template("index.html", **context)
        var.reassign(kgpl.kgval(json_rst))
        server_store.empty_bulk_list()
        # print("kgpl.store.bulkval: ", kgpl.store.bulkval)
        return flask.redirect("/allvars/" + varname)


@app.route("/allvalues", methods=['GET', 'POST'])
def allvals():
    if flask.request.method == 'POST':
        uuid = flask.request.form['uuid']
        return flask.redirect("/allvalues/" + uuid)

    else:
        context = {
            "rst": server_store.availVal()
        }
        return flask.render_template("all_val.html", **context)


@app.route("/allvalues/<uuid>", methods=['GET'])
def specval(uuid):
    value = server_store.GetValue(uuid)
    """
    if value.discriminator == "KGPLList":
        l = value.val
        val = []
        if len(l) == 0:
            empty = "1"
        else:
            empty = "0"
            for item in l:
                if isinstance(item.val, int) or isinstance(item.val, float) or isinstance(item.val, str):
                    mydict = {
                        "display": "1", 
                        "concrete": item.val,
                         "itemID": item.id}
                    val.append(mydict)
                else:
                    mydict = {
                        "display": "0", 
                        "concrete": "KGPLList",
                         "itemID": item.id}
                    val.append(mydict)

                
        context = {
            "empty": empty,
            "UUID": uuid,
            "type": value.discriminator,
            "val": val
        }
    else:
        context = {
            "UUID": uuid,
            "type": value.discriminator,
            "val": value.val
        }"""
    if value:
        # if type(value).__name__ == "KGPLInt" or "KGPLFloat" or "KGPLStr":
        context = {
            "UUID": uuid,
            "type": value.discriminator,
            "url": value.url,
            "val": value.val
        }
        return flask.render_template("specval.html", **context)
    else:
        return flask.abort(404)


@app.route("/wikimap", methods=['GET'])
def ReturnWikiMap():
    pass


#     ss = Session()
#     rst = []
#     fetch = ss.query(BulkLoader.Wikimap)
#     for v in fetch:
#         removed = v.var_id.replace("V", "")
#         rst.append((v.var_id, v.wiki_id, removed))
#     context = {
#         "rst": rst
#     }
#     return flask.render_template("wiki_map.html", **context)


@app.route("/val/<fileid>", methods=['GET', 'POST'])
def ReturnValue(fileid):
    # file_path = os.path.join("val", fileid)
    if flask.request.method == 'GET':
        print("****************************")
        print(server_store.bulkval)
        print("****************************")
        val = server_store.GetValue(fileid)
        if not val:
            return flask.abort(404)
        binary = pickle.dumps(val)
        return binary, 200
    else:
        flask.request.get_data()
        val = pickle.loads(flask.request.data)
        session.make_transient(val)
        print("--------------store value to DB---------------")
        server_store.StoreValues([val, ])
        # print(
        #     "-----------------successfully stored duplicate value to DB ---------------")
        context = {
            "id": fileid,
            "value": "received",
            "url": server_store.selfurl
        }
        return flask.jsonify(**context), 201


@app.route("/var/<varname>", methods=['GET', 'POST'])
def ReturnVariable(varname):
    if flask.request.method == 'GET':
        print("-----------------get var/varname------------------")
        # if s.serverURL:
        #     var = s.GetVariable(varname)
        #     binary = pickle.dumps(var)
        #     return binary, 200
        var = server_store.GetVariable(varname)
        if not var:
            return flask.abort(404)
        binary = pickle.dumps(var)
        return binary, 200
    else:
        print("-----------------post var/varname------------------")

        flask.request.get_data()
        var = pickle.loads(flask.request.data)
        server_store.SetVariable(var)
        context = {
            "variable": "set"
        }
        return flask.jsonify(**context), 201


@app.route("/var", methods=['POST'])
def RegisterVariable():
    print("----------------post /var-------------------")
    flask.request.get_data()
    var = pickle.loads(flask.request.data)
    # if s.serverURL:  # currently dont have parent
    #     return s.RegisterVariable(var)
    # session.make_transient(var)
    server_store.RegisterVariable(var)
    # s.PushValues()
    context = {
        "var_id": var.id,
        "value": "registered"
    }
    return flask.jsonify(**context), 201

# @app.teardown_appcontext
# def shutdown_session(exception=None):
#     Session.remove()
