#!/usr/bin/env python2

from flask import Flask, request

import requests
import random
import json

app = Flask(__name__)
app.debug = True

GOOGLE_URL = 'http://suggestqueries.google.com/complete/search?client=firefox&q=%s'
def complete_google(context):
  q = '+'.join(context)
  r = requests.get(GOOGLE_URL % q)
  j = json.loads(r.text)
  return [s[len(q):] for s in j[1]]

@app.route('/')
def complete():
  # TODO validation
  if not (request.args.get('context') and request.args.get('sources')):
    return ''

  context = request.args.get('context').split()
  sources = request.args.get('sources').split(',')

  completions = []

  if 'google' in sources:
    completions += complete_google(context)

  if len(completions) == 0:
    return ''
  completion = random.sample(completions, 1)[0]
  return completion

application = app
if __name__ == '__main__':
  app.run()
