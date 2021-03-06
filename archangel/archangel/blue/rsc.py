from flask import Blueprint, render_template, abort, send_file, session
import os
import json

rsc = Blueprint('rsc', __name__,
                        template_folder='templates')

with open('language.json', 'rb') as f:
    lang = json.load(f)

config = 'config.json'

with open(config, 'rb') as f:
    info = json.load(f)

info['defaultlanguage'] = info['language']

info['language'] = lang

with open('languagereplacements.json', 'r') as f:
    lang_replacements = json.load(f)

@rsc.route('/rsc/img/avatar/<id>')
def img_avatar(id: int):
    if type(id) == int and str(id) + '.webp' in os.listdir('rsc/img/avatar'):
        return send_file(f'rsc/img/avatar/{str(id)}.webp')
    else:
        return send_file('rsc/img/no_avatar.webp')

@rsc.route('/rsc/css/<css>')
def css(css: str):
    if str(css) + '.css' in os.listdir('rsc/css'):
        return send_file('rsc/css/' + css + '.css')
    else:
        return abort(404)

@rsc.route('/rsc/js/<js>')
def js(js: str):
    if str(js) + '.js' in os.listdir('templates/rsc/js'):
        return render_template('rsc/js/' + js + '.js', session=session, info=info)
    else:
        return abort(404)

@rsc.route('/rsc/img/icon/<icon>')
def img_icons(icon):
    if '.' not in icon and icon + '.webp' in os.listdir('rsc/img/icons'):
        return send_file(f'rsc/img/icons/{str(icon)}.webp')
    else:
        return abort(404)

@rsc.route('/rsc/languagereplacements')
def languagereplacements():
    return render_template('rsc/replacelanguages.js', lang_replacements=lang_replacements)

@rsc.route('/rsc/theme/<theme>')
def theme(theme: str):
    if str(theme) + '.css' in os.listdir('rsc/themes'):
        return send_file('rsc/themes/' + theme + '.css')
    else:
        return send_file('rsc/themes/default.css')