#!/usr/bin/env python
"""
Skeleton Flask application can be run one of these ways:

- Mount this script in a WSGI-compliant server (e.g. Apache+mod_wsgi, uWSGI, etc.)
- Run this script standalone `./app.py <port>` (default port 8888)
"""
from __future__ import with_statement
from __future__ import print_function # python 3.x compatible print()

INTERFACE = '0.0.0.0'
PORT = 8888
ROOT_URI = '/1' # version
CONFIG_FILE = 'app.cfg'

import sys
import datetime, time
import hashlib
import json
import base64
import math
import urllib
from functools import wraps
from pprint import pprint

# logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# flask
from flask import Flask, abort, flash, jsonify, make_response, redirect, Response, render_template, request, session, url_for
app = application = Flask(__name__.split('.')[0]) # application is mod_wsgi export
app.config.from_pyfile(CONFIG_FILE) # load config
app.debug = True

# utils
def requestWantsJson():
    best = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    return request.args.get('format') == 'json' or (best == 'application/json' and
                                                    request.accept_mimetypes[best] > request.accept_mimetypes['text/html'])
def jdumps(obj):
    if not isinstance(obj, dict):
        obj = obj.__dict__
    return json.dumps(obj, 
        default=lambda o: o.isoformat() if (isinstance(o, datetime.datetime) or isinstance(o, datetime.date)) else None,
        sort_keys=True,
        indent=4)

# error handlers
@app.errorhandler(401)
def errorUnauthorized(error):
    return Response(render_template('errors/login_required.html', error=error), 401, {
            'WWW-Authenticate': 'Basic realm="%s"' % app.config['AUTH_REALM'] })
@app.errorhandler(403)
def errorForbidden(error):
    return render_template('errors/access_denied.html'), 403
@app.errorhandler(404)
def errorNotFound(error):
    return render_template('errors/not_found.html'), 404


# routes
@app.route('/')
def index():
    return render_template('index.html')


# started as standalone app (instead of through mod_wsgi)
if __name__ == '__main__':
    import socket
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    print('Starting server on port %d...' % port)
    try:
        if app.debug:
            # disable static asset caching
            app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
        app.run(host=INTERFACE, port=port) # start listener
    except socket.error, ex:
        # port is probably in use
        print('Socket error: %s' % ex)
