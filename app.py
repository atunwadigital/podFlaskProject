import simplejson
from flask import Flask, render_template, g, request, render_template, redirect, jsonify, flash
import couchdb
from datetime import datetime
from couchdb.design import ViewDefinition
import flaskext.couchdb
import secrets
from flask_wtf import FlaskForm
from wtforms import widgets, SelectMultipleField


app = Flask(__name__)
@app.route('/')
def index():
    return render_template("index.html")

"""
CouchDB permanent view
"""
all_docs = ViewDefinition('all_docs','_id','function(doc) { emit(doc._id, doc);}')
docs_by_guid = ViewDefinition('docs_by_guid', 'guid', 'function(doc) { emit(doc.guid, doc);}')
couchDatabase = couchdb.Server(url='http://admin:pthakur%40plenartech.com@localhost:5984/');


def createView( dbConn, designDoc, viewName, mapFunction ):
    data = {
            "_id": f"_design/{designDoc}",
            "views": {
                viewName: {
                    "map": mapFunction
                    }
            },
            "language": "javascript",
            "options": {"partitioned": False }
            }
    dbConn.save( data )




if "pod_config" not in couchDatabase:
    pod_config = couchDatabase.create("pod_config")
    mapFunction = '''function (doc) { 
    if( doc.type == 'word') 
    emit(doc.word, doc); 
    }'''
    createView(pod_config, "config", "between_dates", mapFunction)
else:
    pod_config = couchdb.Database("pod_config")
"""
Retrieve docs
"""
@app.route("/<guid>/docs")
def docs(guid):
    docs = []
    for row in docs_by_guid(g.couch)[guid]:
        docs.append(row.value)
    return simplejson.dumps(docs)

@app.route("/all/docs", methods=['GET', 'POST'])
def alldocs():
    if request.method == "POST":
        selected_pd = request.form.getlist("podlist")
        ct = datetime.now()
        podConfDoc = {"DateModified": str(datetime.now()),"ModifiedTimestamp":str(datetime.now().timestamp()), "SelectedPodlist":selected_pd }
        pod_config.save(podConfDoc)
        flash("Configuration Saved Successfully ","success")
        print(selected_pd)

    docs = []
    for each_doc in pod_config:
        pass
    for row in all_docs(g.couch):
        docs.append(row.value)
    return render_template('itemlist.html',groupings=docs)



"""
 Add doc
 """
# @app.route("/<author_id>/add", methods=['POST'])
# def add_doc(guid):
#     try:
#         # Build doc with posted values
#         doc = { 'guid': guid }
#         doc.update(request.form)
#         # Insert into database
#         g.couch.save(doc)
#         state = True
#     except Exception as e:
#         state = False
#     return simplejson.dumps({'ok': state})

"""
Flask main
"""
if __name__ == "__main__":
    app.config.update(
        DEBUG = True,
        COUCHDB_SERVER = 'http://admin:pthakur%40plenartech.com@localhost:5984/',
        COUCHDB_DATABASE = 'groupings'
    )
    manager = flaskext.couchdb.CouchDBManager()
    manager.setup(app)
    manager.add_viewdef(all_docs)  # Install the view
    manager.add_viewdef(docs_by_guid)  # Install the view
    secret = secrets.token_urlsafe(32)
    app.secret_key = secret
    app.run(host='0.0.0.0', port=5000)
    # app.run(debug=True,host='0.0.0.0', port=5000)