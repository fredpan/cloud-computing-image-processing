import json


def http_response(code, msg):
    return json.dumps([{code: msg}])
