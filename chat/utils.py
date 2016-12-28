import json

from django.http import HttpResponse


def render_json(dic={}):
    if type(dic) is not dict:
        dic = {
            'result': True,
            'message': dic
        }
    return HttpResponse(json.dumps(dic))
