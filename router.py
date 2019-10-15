from flask import Flask

import model_by_inn

app = Flask(__name__)


@app.route('/inn/<inn>/')
def arbitr_by_inn(inn):
    result = model_by_inn.return_arb(inn)
    return ""


@app.route('/')
def index():
    return 'Main page'
