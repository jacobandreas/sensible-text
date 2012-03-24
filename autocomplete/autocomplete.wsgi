#!/usr/bin/env python2

from flask import Flask, request

import requests
import random
import json
import nltk

app = Flask(__name__)
app.debug = True

GOOGLE_URL = 'http://suggestqueries.google.com/complete/search?client=firefox&q=%s'
def complete_google(context):
  q = '+'.join(context)
  r = requests.get(GOOGLE_URL % q)
  j = json.loads(r.text)
  #return [s[len(q):] for s in j[1]]
  completions = []
  for s in j[1]:
    if len(s.split()) <= len(context):
      continue
    completion = s[len(q):]
    if not completion[0] == ' ':
      continue
    completions.append(completion[1:])
  return completions

#lm = nltk.model.ngram
austen_file = open('/home/jacob/public_html/autocomplete.jacobandreas.net/autocomplete/austen.txt')
austen_lines = '\n'.join(austen_file.readlines())
austen_file.close()
austen_toks = nltk.word_tokenize(austen_lines)
austen_ngram = nltk.model.NgramModel(3, austen_toks)
print('finished loading austen.txt')
def complete_austen(context):
  completions = []
  for i in range(3):
    suggestion = austen_ngram.generate(3, context)
    completions.append(' '.join(suggestion[len(context):]))
  return completions

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

  if 'austen' in sources:
    completions += complete_austen(context)

  if len(completions) == 0:
    return ''
  completion = random.sample(completions, 1)[0]
  return completion

application = app
if __name__ == '__main__':
  app.run()
