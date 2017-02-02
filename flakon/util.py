import os
import mimetypes
import json
import yaml
# replace requests by httplib
import requests
from werkzeug.exceptions import HTTPException
from flask import jsonify, abort


_JSON_TYPES = ('application/vnd.api+json', 'application/json')
_YAML_TYPES = ('application/x-yaml', 'text/yaml')

if '.yaml' not in mimetypes.types_map:
    mimetypes.types_map['.yaml'] = 'application/x-yaml'


def _decoder(mime):
    if mime in _YAML_TYPES:
        return yaml.load
    # we'll just try json
    return json.loads


def get_content(url):
    if os.path.exists(url):
        mime = mimetypes.guess_type(url)[0]
        with open(url) as f:
            data = f.read()
            return _decoder(mime)(data)
    else:
        resp = requests.get(url)
        content_type = resp.header.get('Content-Type', 'application/json')
    return _decoder(content_type)(requests.get(url).content)


def error_handling(error):
    if isinstance(error, HTTPException):
        result = {'code': error.code, 'description': error.description,
                  'message': str(error)}
    else:
        description = abort.mapping[500].description
        result = {'code': 500, 'description': description,
                  'message': str(error)}

    resp = jsonify(result)
    resp.status_code = result['code']
    return resp