import json
import logging

import flask

import model


class ControllerByInn():
    def __init__(self, inn):
        self.inn = inn
        self.mod = model.ModelByInn(self.inn)

    def render(self):
        try:
            result = self.mod.return_arb()
        except Exception as e:
            logging.error(e)
            result = e.args
        if isinstance(result, list):
            # result.insert(0, {"Success": 1})
            return flask.Response(json.dumps(result, ensure_ascii=False), mimetype='application/json')
        elif isinstance(result, tuple):
            exeption_result = {"Success": 0, "errors": [x for x in result]}
            return flask.Response(json.dumps(exeption_result, ensure_ascii=False), mimetype='application/json')
        elif isinstance(result, Exception):
            exeption_result = {"Success": 0, "errors": result.args}
            return flask.Response(json.dumps(exeption_result, ensure_ascii=False), mimetype='application/json')
        else:
            return flask.Response(json.dumps([], ensure_ascii=False), mimetype='application/json')
