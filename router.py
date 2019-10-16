import flask
from flask import Flask

import controller

app = Flask(__name__)


# @app.route('/inn/<inn>/')
# def arbitr_by_inn(inn):
#     c = controller.ControllerByInn(inn)
#     return c.response_by_inn()

@app.route('/inn/', methods=['post'])
def arbitr_by_inn_post():
    inn = flask.request.form.get('inn')
    c = controller.ControllerByInn(inn)
    return c.response_by_inn()

@app.route('/')
def index():
    return flask.render_template("index.html")
