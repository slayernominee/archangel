from flask import Blueprint, render_template, abort, send_file, session, request
import os
import json
from util import stream

api = Blueprint('api', __name__, template_folder='templates', url_prefix='/api')

with open('rsc/api.json', 'rb') as f:
    apiinfoj = json.load(f)

with open('language.json', 'rb') as f:
    lang = json.load(f)

with open('api_tokens.json', 'r') as f:
    api_tokens = json.load(f)

config = 'config.json'

with open(config, 'rb') as f:
    info = json.load(f)

info['defaultlanguage'] = info['language']

info['language'] = lang

@api.route('/')
def apiinfo():
    return render_template('pages/apiinfo.html', apiinfo=apiinfoj, session=session, info=info)

@api.route('/search', methods=['POST'])
def search():
    jd = request.get_json(force=True)
    query = str(jd['query'])
    results = stream.searchSeries(query)
    result = {
        "code": 200,
        "results": results,
        "query": query
    }
    return result

@api.route('/upload/stream', methods=['POST'])
def upload_stream():
    jd = request.get_json(force=True)
    token = jd['token']
    if token not in api_tokens['unlimited']:
        return abort(403)
    series = jd['series']
    season = jd['season']
    episode = jd['episode']
    language = jd['language']
    link = jd['link']
    provider = jd['provier']
    if 'name' in jd:
        name = jd['name']
    else:
        name = ''
    if 'description' in jd:
        description = jd['description']
    else:
        description = ''
    stream.createEpisodeWSeries(series, season, language, link, provider, episode, name, description)
    return 'stream created'