import json


def http_response(code, msg):
    '''

    :param code: the http error code
    :param msg: the costomized mssage
    :return: the formatted json
    '''
    return json.dumps([{code: msg}])
