import json

import flask
from flask import Flask

import model_by_inn

app = Flask(__name__)


@app.route('/inn/<inn>/')
def arbitr_by_inn(inn):
    try:
        result = model_by_inn.return_arb(inn)
        return flask.Response(json.dumps(result), mimetype='application/json')
    except Exception as e:
        return e


@app.route('/')
def index():
    return 'Main page'
