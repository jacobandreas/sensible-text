import os
import json
from completer import Completer
from flask import Flask, Response, send_from_directory, request

app = Flask(__name__)

cpl = Completer()

app.logger.debug("READY.")

@app.route('/')
def index():
  return send_from_directory(os.path.join(app.root_path, 'static'),
                             'index.html') 

@app.route('/complete')
def complete():

  sources = request.args.get('sources')
  context = request.args.get('context')

  if not (sources and context):
    return Response('bad request', 404)

  sources = sources.split(',')
  context = context.lower().split()

  completions = cpl.complete(sources, context)

  return Response(json.dumps(completions),
                  mimetype='application/json')

@app.route('/debug')
def debug():
  return str(app.debug)

if __name__ == '__main__':
  app.run(debug=True)
