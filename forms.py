import simplejson
from flask import Flask, render_template, g, request, render_template, redirect, jsonify
import couchdb
from datetime import datetime
from couchdb.design import ViewDefinition
import flaskext.couchdb
from flask_wtf import FlaskForm
from wtforms import widgets, SelectMultipleField