#!/usr/bin/env python2

from flask import Flask, request

import requests
import random
import json
import nltk
import re

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

#austen_file = open('/home/jacob/public_html/autocomplete.jacobandreas.net/autocomplete/austen.txt')
austen_file = open('austen.txt')
austen_lines = '\n'.join(austen_file.readlines())
austen_file.close()
austen_toks = nltk.word_tokenize(austen_lines)
austen_ngram = nltk.model.NgramModel(3, austen_toks)
print('finished loading austen.txt')
def complete_austen(context):
  completions = []
  for i in range(3):
    suggestion = austen_ngram.generate(1, context)
    completions.append(' '.join(suggestion[len(context):]))
  return completions

#joyce_file = open('/home/jacob/public_html/autocomplete.jacobandreas.net/autocomplete/joyce.txt')
joyce_file = open('joyce.txt')
joyce_lines = '\n'.join(joyce_file.readlines())
joyce_file.close()
joyce_toks = nltk.word_tokenize(joyce_lines)
joyce_ngram = nltk.model.NgramModel(3, joyce_toks)
print('finished loading joyce.txt')
def complete_joyce(context):
  completions = []
  for i in range(3):
    suggestion = joyce_ngram.generate(1, context)
    completions.append(' '.join(suggestion[len(context):]))
  return completions

PARSELY_URL = 'http://simon.parsely.com:8983/solr/goldindex2/select/?wt=json&q=%s'
def complete_parsely(context):
  ncontext = [w for w in context if w[0].isupper()]
  if not ncontext:
    return []
  q = '+'.join(ncontext)
  r = requests.get(PARSELY_URL % q)
  j = json.loads(r.text)
  docs = j['response']['docs']
  articles = [doc['full_content'] for doc in docs]
  text = ' '.join(articles)
  rexp = ' '.join(context) + r'((\s\w+){1,3})'
  matches = re.findall(rexp, text)
  return [m[0][1:] for m in matches]

trigram_pool = list()
def complete_stranger():
  take = min(len(trigram_pool), 3)
  samples = random.sample(trigram_pool, take)
  return [' '.join(sample) for sample in samples]

@app.route('/')
def complete():
  global trigram_pool
  if not (request.args.get('context') and request.args.get('sources')):
    return ''

  context = request.args.get('context').split()
  sources = request.args.get('sources').split(',')

  trigram_pool.append(context)
  trigram_pool = trigram_pool[-15:]

  completions = []

  if 'google' in sources:
    completions += complete_google(context)

  if 'austen' in sources:
    completions += complete_austen(context)

  if 'joyce' in sources:
    completions += complete_joyce(context)

  if 'parsely' in sources:
    completions += complete_parsely(context)

  if 'strangers' in sources:
    completions += complete_stranger()

  if len(completions) == 0:
    return ''
  completion = random.sample(completions, 1)[0]
  return completion

application = app
if __name__ == '__main__':
  app.run()
