import json
import requests
import nltk
import random

class GoogleCompleter:
  GOOGLE_URL = 'http://suggestqueries.google.com/complete/search?client=firefox&q=%s'

  def complete(self, context):
    q = '+'.join(context)
    sq = ' '.join(context)
    r = requests.get(self.GOOGLE_URL % q)
    j = json.loads(r.text)
    completions = []
    for s in j[1]:
      # if prefix doesn't match query, this is a bad completion
      # note that == unboxes unicode utf8 properly, but `is` doesn't
      if not (s[:len(q)] == sq):
        continue
      # take everything after the query
      completion = s[len(q):]
      # ignore cases where Google is trying to finish our word
      if not (len(completion) > 0 and completion[0] == ' '):
        continue
      # all checks pass: this is a good completion
      completions.append(completion[1:])
    return completions

class AustenCompleter:
  AUSTEN_FILENAME = 'resources/austen.txt'
  MODEL_ORDER = 3
  COMPLETION_SIZE = 3
  COMPLETION_COUNT = 3

  def __init__(self):
    austen_file = open(self.AUSTEN_FILENAME)
    austen_lines = '\n'.join(austen_file.readlines())
    austen_file.close()
    austen_toks = nltk.word_tokenize(austen_lines)
    austen_toks_nopunct = [tok for tok in austen_toks if not
        self.punctuation(tok)]
    # TODO logging?
    self.model = nltk.model.NgramModel(self.MODEL_ORDER, austen_toks_nopunct)

  def punctuation(self, token):
    return token in ('.', ',', '?', '!', ';', ':', "''", "``", "'")

  def complete(self, context):
    completions = []
    for i in range(self.COMPLETION_COUNT):
      generated = self.model.generate(self.COMPLETION_SIZE, context)
      # chop to keep only generated material
      completion = ' '.join(generated[len(context):])
      completions.append(completion)
    return completions

# This appears to have been taken down after the hackathon, so I won't
# reimplement it

# class ParselyCompleter:
#   PARSELY_URL = 'http://simon.parsely.com:8983/solr/goldindex2/select/?wt=json&q=%s'
#   def complete(self, context):
#     q = '+'.join(context)
#     r = requests.get(PARSELY_URL % q)
#     j = json.loads(r.text)
#     docs = j['response']['docs']
# etc.

class StrangerCompleter:
  POOL_SIZE = 15
  COMPLETION_COUNT = 3

  def __init__(self):
    self.pool = list()

  def update(self, context):
    self.pool.append(context)
    self.pool = self.pool[-self.POOL_SIZE:]

  def complete(self, context):
    count = min(len(self.pool), self.COMPLETION_COUNT)
    samples = random.sample(self.pool, count)
    return [' '.join(sample) for sample in samples]

class Completer:

  def __init__(self):
    self.completers = {
      'google': GoogleCompleter(),
      'austen': AustenCompleter(),
      'stranger': StrangerCompleter(),
    }
    self.stranger_completer = self.completers['stranger']
    self.default_completer = self.completers['stranger']

  def complete(self, sources, context):
    completions = []
    for source in sources:
      if source in self.completers:
        completions += self.completers[source].complete(context)
    if len(completions) == 0:
      completions += self.default_completer.complete(context)
    self.stranger_completer.update(context)
    random.shuffle(completions)
    return completions
