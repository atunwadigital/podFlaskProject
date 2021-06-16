import simplejson
from flask import Flask, render_template, g, request, render_template, redirect, jsonify
import couchdb
from datetime import datetime
from couchdb.design import ViewDefinition
import flaskext.couchdb
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

"""
Retrieve docs
"""
@app.route("/<guid>/docs")
def docs(guid):
    docs = []
    for row in docs_by_guid(g.couch)[guid]:
        docs.append(row.value)
    return simplejson.dumps(docs)

@app.route("/all/docs")
def alldocs():
    docs = []
    for row in all_docs(g.couch):
        docs.append(row.value)
    return render_template('itemlist.html',groupings=docs)


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

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
    app.run(host='0.0.0.0', port=5000)
    # app.run(debug=True,host='0.0.0.0', port=5000)