#!/usr/bin/env python
from __future__ import print_function
import urllib
import httplib
import logging
import json

logger = logging.getLogger(__name__)

LOG = True
SSL = True
SERVER = 'api.trello.com'
BASE_URI = '/1'

_connection = None
def getConnection():
	global _connection
	if not _connection:
		_connection = (httplib.HTTPSConnection if SSL else httplib.HTTPConnection)(SERVER)
	return _connection

class APIException(Exception):
	def __init__(self, code, error, body):
		self.code = code
		self.error =error
		self.body = body
	def __repr__(self):
		return "%d: %s" % (self.code, self.error)

def request(method, uri, query={}, body={}, headers={}, debug=False):
	conn = getConnection()

	url = BASE_URI + ('%s?%s' % (
		uri, urllib.urlencode([ (k,v) for k,v in query.items() if query.items() ]) if query else None) \
		if query else uri )

	acceptType = 'application/json'
	encodedBody = json.dumps(body)

	# send request
	if LOG:
		logger.debug('Request: %s %s %s' % (method, url, encodedBody))
	requestHeaders = {
		'Accept': acceptType,
		'Content-Type': acceptType }
	requestHeaders.update(headers)
	conn.request(method, uri, body=encodedBody, headers=requestHeaders)

	# get response
	resp = conn.getresponse()
	body = resp.read() # read() has to be called for subsequent keepalive requests
	if not (199 < resp.status < 300): # not a 2xx success response
		logger.error('Request failed: (%d) %s %s' % (resp.status, resp.reason, body))
		raise APIException(resp.status, resp.reaspon, body)
	if LOG:
		# dump response headers
		logger.debug('    %d %s' % (resp.status, resp.reason))
		for header in resp.getheaders():
			logger.debug('    %s: %s' % header)

	# decode response message
	contentType = resp.getheader('Content-Type')
	if not acceptType in contentType: # server returned unexpected response entity
		logger.error('Response type is "%s", but "%s" was expected' % (contentType, acceptType))
		raise APIException(0, 'Unexpected return content type: %s' % contentType, body)
	obj = json.loads(body)
	if LOG:
		# dump response body (decoded)
		for line in json.dumps(obj, sort_keys=True, indent=4).splitlines():
			logger.debug('    ' + line)
	return obj

import unittest
class TestRequest(unittest.TestCase):
	def setUp(self): pass
	def test_request(self):
		request('GET', '/boards/xyz', query={
			'x': 1,
			'y': 'moo' })
		self.assertEquals(1, 2)

if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG)
	unittest.main()
