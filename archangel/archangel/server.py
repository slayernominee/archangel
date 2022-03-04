#!/bin/python
# copyright by Marcel Rieger

import datetime
import json
import os
import random
import pyotp
import smtplib
import string
from email.message import EmailMessage
from flask import (Flask, abort, make_response, redirect, render_template,
                   request, send_file, session)

from blue.rsc import rsc
from util import accounts, notifications, stream, watch

app = Flask(__name__)

SESSION_LIFETIME_DAYS = 30
MAX_UPLOAD_SIZE_MB = 15

app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=SESSION_LIFETIME_DAYS)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * MAX_UPLOAD_SIZE_MB

app.secret_key = os.urandom(4096)

app.register_blueprint(rsc)

if os.path.isfile('config.json'):
    config = 'config.json'
elif os.path.isfile('server/config.json'):
    os.chdir('server')
    config = 'config.json'
else:
    print('config file not found!!!')
    exit()
with open(config, 'rb') as f:
    info = json.load(f)

info['defaultlanguage'] = info['language']

with open('language.json', 'rb') as f:
    lang = json.load(f)

info['language'] = lang

if info['auto_spotlight'] == True:
    sI = stream.getUnstructuredSeriesIndex()
    random.shuffle(sI)
    if len(sI) >= 32:
        spotlight = {
        "1": [],
        "2": [],
        "3": [],
        "4": []
        }
        for i in range(0, 8):
            spotlight['1'].append(sI[i])
        for i in range(8, 16):
            spotlight['2'].append(sI[i])
        for i in range(8*2, 8*3):
            spotlight['3'].append(sI[i])
        for i in range(8*3, 8*4):
            spotlight['4'].append(sI[i])
    elif len(sI) >= 24:
        spotlight = {
        "1": [],
        "2": [],
        "3": []
        }
        for i in range(0, 8):
            spotlight['1'].append(sI[i])
        for i in range(8, 16):
            spotlight['2'].append(sI[i])
        for i in range(8*2, 8*3):
            spotlight['3'].append(sI[i])
    elif len(sI) >= 16:
        spotlight = {
        "1": [],
        "2": []
        }
        for i in range(0, 8):
            spotlight['1'].append(sI[i])
        for i in range(8, 16):
            spotlight['2'].append(sI[i])
    elif len(sI) >= 8:
        spotlight = {
        "1": []
        }
        for i in range(0, 8):
            spotlight['1'].append(sI[i])
    elif len(sI) >= 4:
        spotlight = {
        "1": [sI[0], sI[1], sI[2], sI[3]]
        }
    else:
        spotlight = []
else:
    with open('spotlight.json', 'rb') as f:
        spotlight = json.load(f)

def reloadSpotlight():
    global spotlight
    if info['auto_spotlight'] == True:
        sI = stream.getUnstructuredSeriesIndex()
        random.shuffle(sI)
        if len(sI) >= 32:
            spotlight = {
            "1": [],
            "2": [],
            "3": [],
            "4": []
            }
            for i in range(0, 8):
                spotlight['1'].append(sI[i])
            for i in range(8, 16):
                spotlight['2'].append(sI[i])
            for i in range(8*2, 8*3):
                spotlight['3'].append(sI[i])
            for i in range(8*3, 8*4):
                spotlight['4'].append(sI[i])
        elif len(sI) >= 24:
            spotlight = {
            "1": [],
            "2": [],
            "3": []
            }
            for i in range(0, 8):
                spotlight['1'].append(sI[i])
            for i in range(8, 16):
                spotlight['2'].append(sI[i])
            for i in range(8*2, 8*3):
                spotlight['3'].append(sI[i])
        elif len(sI) >= 16:
            spotlight = {
            "1": [],
            "2": []
            }
            for i in range(0, 8):
                spotlight['1'].append(sI[i])
            for i in range(8, 16):
                spotlight['2'].append(sI[i])
        elif len(sI) >= 8:
            spotlight = {
            "1": []
            }
            for i in range(0, 8):
                spotlight['1'].append(sI[i])
        elif len(sI) >= 4:
            spotlight = {
            "1": [sI[0], sI[1], sI[2], sI[3]]
            }
        else:
            spotlight = []
    else:
        with open('spotlight.json', 'rb') as f:
            spotlight = json.load(f)

@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
def home():
    if info['public_home'] == False and 'id' not in session: return abort(401)
    seriesIndex = stream.getSeriesIndex()
    genreIndex = stream.getGenreIndex()
    newestCreated = stream.getNewestCreatedSeries(count=15)
    newestCreatedEpisodes = stream.getNewestCreatedEpisodes(count=20)
    reqs = stream.getRequests(count=8)
    return render_template('pages/home.html', info=info, session=session, reqs=reqs, seriesIndex=seriesIndex, spotlight=spotlight, genreIndex=genreIndex, newestCreated=newestCreated, newestCreatedEpisodes=newestCreatedEpisodes)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if info['public_search'] == False and 'id' not in session: return abort(401)
    if request.method == 'POST':
        query = request.form['query']
        results = stream.searchSeries(query)
        result = ''
        for r in results:
            result += f"""<a href="/stream/{r['id']}/1/1" style="text-decoration: none;">
        <div class=\"lent result_entry\""""
            if r['banner'].startswith('http'):
                result += f""" style="background-image: url('{r['banner']}');\""""
            result += f"><img src=\"{r['image']}\">"
            if r['name'].startswith("-") and r["name"][1] in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                result += f"<h2>{r['name'][1:]}<br>"
            else:
                result += f"<h2>{r['name']}<br>"
            
            result += f"<span class='description'>{r['description'][:200]}</span>"
            result += '</h2>'

            result += '<div style="float: right;">'
            result += '</div></div></a>'

        return result
    else:
        return render_template('pages/search.html', info=info, session=session, seriesIndex=str(stream.getUnstructuredSeriesIndex()))

# Index
@app.route('/index', methods=['GET'])
def index():
    if info['public_index'] == False and 'id' not in session: return abort(401)
    if 'sort' in request.args and request.args['sort'].lower() in ['genre', 'genres']:
        seriesIndex = stream.getSeriesIndex_Genre()
        return render_template('pages/index/index.html', session=session, info=info, series=seriesIndex)
    elif 'sort' in request.args and request.args['sort'].lower() in ['year', 'startyear']:
        seriesIndex = stream.getSeriesIndex_StartYear()
        return render_template('pages/index/index.html', session=session, info=info, series=seriesIndex)
    else:
        seriesIndex = stream.getSeriesIndex()
        return render_template('pages/index/index.html', session=session, info=info, series=seriesIndex)

@app.route('/random', methods=['GET', 'POST'])
def random_series():
    id = stream.getRandomSeriesId()
    return redirect('/stream/' + str(id) + '/1/1')

@app.route('/genre/<genre>')
def genre(genre: str):
    series = stream.getSeriesWithGenre(genre)
    return render_template('pages/genre.html', info=info, session=session, genre=genre, series=series)

@app.route('/studio/<studio>')
def studio(studio: str):
    series = stream.getSeriesWithStudio(studio)
    return render_template('pages/genre.html', info=info, session=session, genre=studio, series=series)

@app.route('/age/<age>')
def age(age: int):
    series = stream.getSeriesWithAge(age)
    return render_template('pages/genre.html', info=info, session=session, genre=f'Age: {age}', series=series)

@app.route('/subgenre/<genre>')
def subgenre(genre: str):
    series = stream.getSeriesWithSubGenre(genre)
    return render_template('pages/genre.html', info=info, session=session, genre=genre, series=series)

@app.route('/staff/<staff>')
def staff(staff: str):
    series = stream.getSeriesWithStaff(staff)
    return render_template('pages/genre.html', info=info, session=session, genre=staff, series=series)

@app.route('/country/<country>')
def country(country: str):
    series = stream.getSeriesWithCountry(country)
    return render_template('pages/genre.html', info=info, session=session, genre=country, series=series)

@app.route('/notifications')
def notification_page():
    if 'id' not in session: return abort(401)
    nots = notifications.getNewestNotifications(session['id'], count=200)
    notis = []
    for noti in nots:
        notis.append({
            "id": noti.id,
            "type": noti.type,
            "title": noti.title,
            "text": noti.text,
            "duration": noti.duration,
            "buttons": noti.buttons,
            "date": noti.date
        })
    return render_template('pages/notifications.html', info=info, session=session, notis=notis)

@app.route('/requests', methods=['GET', 'POST'])
@app.route('/anfragen', methods=['GET', 'POST'])
def requests():
    reqs = stream.getRequests()
    if 'id' in session:
        uvotes = stream.getUserRequestVotes(session['id'])
    else:
        uvotes = []
    if 'id' in session and request.method == 'POST':
        if 'up' in request.form:
            req = int(request.form['up'])
            stream.voteUpRequest(req, session['id'])
            return 'ok'
        elif 'down' in request.form:
            req = int(request.form['down'])
            stream.voteDownRequest(req, session['id'])
            return 'ok'
        elif 'delete' in request.form:
            if session['perms']['links'] == True:
                req = int(request.form['delete'])
                stream.disableRequest(req)
                return 'ok'
            else:
                return abort(403)
        elif 'name' in request.form:
            name = str(request.form['name'])
            stream.createNewRequest(name, session['id'])
            notifications.newNotification(session['id'], 5000, 0, 'new series request', 'Request was send', 'Your request was successfully send', type='success')
            return redirect('/requests')
        else:
            return abort(400)
    return render_template('pages/requests.html', session=session, info=info, reqs=reqs, uvotes=uvotes)

# Beta
@app.route('/settheme/<theme>', methods=['GET', 'POST'])
def set_theme(theme):
    session['theme'] = theme
    return redirect('/home')

@app.route('/setlanguage/<language>', methods=['GET', 'POST'])
def set_language(language):
    if language not in accounts.available_languages:
        return abort(400)
    else:
        session['language'] = language
        return redirect('/home')

# account area
@app.route('/account')
def account():
    if 'id' not in session: return abort(401)
    return render_template('pages/account/account.html', session=session, info=info)

@app.route('/account/settings', methods=['GET', 'POST'])
def account_setting():
    if 'id' not in session: return abort(401)
    if request.method == 'POST':
        if 'value' in request.form and 'key' in request.form:
            key = request.form['key']
            value = request.form['value']
            key = str(key).lower()
            if key in ['language']:
                value = str(value).lower()
                if value not in accounts.available_languages:
                    return redirect('/account/settings')
                else:
                    accounts.updateLanguage(session['id'], value)
                    session['language'] = value
                    return redirect('/account/settings')
            elif key in ['description']:
                accounts.updateDescription(session['id'], value)
                session['description'] = value
                return redirect('/account/settings')
            elif key in ['theme']:
                accounts.updateTheme(session['id'], value)
                session['theme'] = value
                return redirect('/account/settings')
            elif key in ['name']:
                accounts.updateName(session['id'], value)
                session['name'] = value
                return redirect('/account/settings')
            elif key in ['location']:
                accounts.updateLocation(session['id'], value)
                session['location'] = value
                return redirect('/account/settings')
            elif key in ['image']:
                accounts.updateImage(session['id'], value)
                session['image'] = value
                return redirect('/account/settings')
            elif key in ['banner']:
                accounts.updateBanner(session['id'], value)
                session['banner'] = value
                return redirect('/account/settings')
            elif key in ['username']:
                return 'comming soon'
            else:
                return 'currently not available!!!'
        elif 'pwd' in request.form and 'pwd_old' in request.form:
            newPwd = request.form['pwd']
            oldPwd = request.form['pwd_old']
            if accounts.checkUserLogin(session['mail'], oldPwd):
                accounts.updatePassword(session['id'], newPwd)
                session.clear()
                return str('pwd changed')
            else:
                return abort(403)
        elif 'code' in request.form:
            code = str(request.form['code']).lower()
            correct_code = str(pyotp.TOTP(session['fa_temp']['base']).now()).lower()
            if code == correct_code:
                accounts.updateFaCode(session['id'], session['fa_temp']['base'])
                session['2fa'] = code
                notifications.newNotification(type='success', user=session['id'], duration=5000, sender=0, reason='2fa code setup', title='2FA Code Setup', text='You have successfully setup 2fa codes for your account!')
                return redirect('/account/settings')
            else:
                notifications.newNotification(session['id'], 5000, 0, 'false 2fa code', 'Invalid 2Fa Code', 'The Code you have entered was wrong!', type='error', inbox=False)
                return redirect('/account/settings?special=2fa')
        else:
            return abort(400)
    else:
        if 'special' in request.args and request.args['special'].lower() in ['2fa']:
            base = pyotp.random_base32()
            t = pyotp.TOTP(base)
            fa = {
                "base": base,
                "link": t.provisioning_uri(name=info['name'], issuer_name=info['name'], image=info['favicon'])
            }
            session['fa_temp'] = fa
            return render_template('pages/account/settings_2fa.html', session=session, info=info, fa=fa)
        else:
            return render_template('pages/account/settings.html', session=session, info=info)

@app.route('/account/watched', methods=['GET', 'POST'])
def account_watched():
    if 'id' not in session: return abort(401)
    return 'comming soon!'

@app.route('/account/subscribed', methods=['GET', 'POST'])
@app.route('/account/subscribtions', methods=['GET', 'POST'])
def account_subscribed():
    if 'id' not in session: return abort(401)
    subscribed_series = watch.getAllSubscribedSeries(session['id'])
    subscribed_series = stream.getManySeries(subscribed_series)

    return render_template('pages/account/subscribed.html', session=session, info=info, series=subscribed_series)

# streaming
@app.route('/stream/<seriesId>', methods=['GET', 'POST'])
def stream_series(seriesId):
    if info['public_stream_series'] == False and 'id' not in session: return abort(401)
    if seriesId.lower() in ['add']:
        if 'id' not in session: return abort(401)
        if session['perms']['links'] == True:
            if request.method == 'POST':
                name = str(request.form['name'])
                if name[0] in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
                    name = '-' + name
                description = request.form['description']
                image = request.form['image']
                banner = request.form['banner']
                genres = request.form['genres'].split(",")
                stuff = request.form['stuff'].split(",")
                subgenres = request.form['subgenres'].split(",")
                studio = request.form['studio']
                country = request.form['country']
                if 'age' in request.form and request.form['age'] != '':
                    age = int(request.form['age'])
                else:
                    age = -1
                if 'startyear' in request.form and request.form['startyear'] != '':
                    startyear = int(request.form['startyear'])
                else:
                    startyear = -1
                if 'endyear' in request.form and request.form['endyear'] != '':
                    endyear = int(request.form['endyear'])
                else:
                    endyear = -1
                alternative = request.form['alternative']
                seriesId = stream.createSeries(name=name, image=image, banner=banner, description=description, studio=studio, genres=genres, stuff=stuff, country=country, alternativ=alternative.split(','), age=age, startyear=startyear, endyear=endyear, subgenres=subgenres)
                reloadSpotlight()
                return redirect(f'/stream/{seriesId}')
            else:
                return render_template('pages/stream/add_series.html', session=session, info=info)
        else:
            return abort(403)
    elif seriesId.lower() in ['edit']:
        if 'perms' not in session: return abort(401)
        if session['perms']['links'] != True: return abort(403)
        if request.method == 'POST':
            if 'id' not in request.form: return abort(400)
            seriesId = int(request.form['id']) # will cause 500 if its not int

            series = stream.getSeries(seriesId)

            name = request.form['name']
            description = request.form['description']
            image = request.form['image']
            banner = request.form['banner']
            country = request.form['country']
            studio = request.form['studio']
            age = request.form['age']
            genres = request.form['genres'].split(',')
            subgenres = request.form['subgenres'].split(',')
            alternative = request.form['alternative'].split(',')
            staff = request.form['staff'].split(',')
            startyear = request.form['startyear']
            endyear = request.form['endyear']

            if name[0] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']: name = '-' + name

            if name != series['name']: stream.seriesUpdateName(seriesId, name)
            if description != series['description']: stream.seriesUpdateDescription(seriesId, description)
            if image != series['image']: stream.seriesUpdateImage(seriesId, image)
            if banner != series['banner']: stream.seriesUpdateBanner(seriesId, banner)
            if country != series['country']: stream.seriesUpdateCountry(seriesId, country)
            if studio != series['studio']: stream.seriesUpdateStudio(seriesId, studio)
            if age != series['age']: stream.seriesUpdateAge(seriesId, age)
            if startyear != series['startyear']: stream.seriesUpdateStartYear(seriesId, startyear)
            if endyear != series['endyear']: stream.seriesUpdateEndYear(seriesId, endyear)

            stream.seriesUpdateStaff(seriesId, staff)
            stream.seriesUpdateGenres(seriesId, genres)
            stream.seriesUpdateSubgenres(seriesId, subgenres)
            stream.seriesUpdateAlternative(seriesId, alternative)


            return redirect(f'/stream/{seriesId}')

        else:
            if 'id' not in request.args: return abort(400)
            seriesId = int(request.args['id']) # will cause 500 if its not int
            series = stream.getSeries(seriesId)
            return render_template('pages/stream/edit_series.html', session=session, info=info, series=series)
    elif seriesId.lower() in ['delete', 'remove']:
        if 'id' not in session: return abort(401)
        if session['perms']['admin'] != True: return abort(403)
        if request.method != 'POST': return abort(405)
        id = int(request.form['id'])
        stream.deleteSeries(id)
        reloadSpotlight()
        return 'ok'
    else:
        if str(seriesId[0]) in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            series = stream.getSeries(seriesId)
        else:
            series = stream.getSeriesByName(seriesId)
        if series == None: abort(404)
        if 'id' in session:
            subscribed = watch.isSubscribed(session['id'], series['id'])
        else:
            subscribed = False
        seriesScore = stream.getTotalScore_Series(seriesId)
        return render_template('pages/stream/series.html', info=info, session=session, seriesinfo=series, subscribed=subscribed, seriesScore=seriesScore)

@app.route('/stream/<series>/<season>', methods=['GET', 'POST'])
@app.route('/stream/<series>/Season-<season>', methods=['GET', 'POST'])
@app.route('/stream/<series>/Staffel-<season>', methods=['GET', 'POST'])
def stream_season(series, season):
    if info['public'] == False and 'id' not in session: return abort(401)
    if season.lower() == 'add':
        if 'id' not in session:
            return abort(401)
        if session['perms']['links'] == True:
            if str(series[0]) in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
                series = stream.getSeries(series)
            else:
                series = stream.getSeriesByName(series)
            if request.method == 'POST':
                number = int(request.form['number'])
                if str(number) in series['seasons']:
                    return abort(400)
                name = request.form['name']
                description = request.form['description']
                series = series['id']
                stream.createSeason(series, number=number, name=name, description=description)
                return redirect(f'/stream/{series}/{number}')
            else:
                return render_template('pages/stream/add_season.html', session=session, info=info, series=series)
        else:
            return abort(403)
    elif season.lower() in ['delete', 'remove']:
        if 'id' not in session:
            return abort(401)
        if session['perms']['links'] == True:
            seasonNumber = request.form['season']
            stream.deleteStructuredSeason(series, seasonNumber)
            return 'deleted'
        else:
            return abort(403)
    seriesId = series
    seasonNumber = season

    if str(seriesId[0]) in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
        series = stream.getSeries(seriesId)
    else:
        series = stream.getSeriesByName(seriesId)
    if str(season) not in series['seasons']: return abort(404)
    season = stream.getSeason(series['seasons'][str(season)]['id'])

    if 'id' in session:
        subscribed = watch.isSubscribed(session['id'], series['id'])
    else:
        subscribed = False
    seriesScore = stream.getTotalScore_Series(seriesId)
    return render_template('pages/stream/season.html', info=info, session=session, seriesinfo=series, season=season, seasonNumber=seasonNumber, subscribed=subscribed, seriesScore=seriesScore)

@app.route('/stream/<series>/<season>/<episode>', methods=['GET', 'POST'])
@app.route('/stream/<series>/Season-<season>/<episode>', methods=['GET', 'POST'])
@app.route('/stream/<series>/Staffel-<season>/<episode>', methods=['GET', 'POST'])
@app.route('/stream/<series>/Season-<season>/Episode-<episode>', methods=['GET', 'POST'])
@app.route('/stream/<series>/Staffel-<season>/Episode-<episode>', methods=['GET', 'POST'])
def stream_episode(series, season, episode):
    if info['public'] == False and 'id' not in session: return abort(401)
    if episode.lower() == 'add':
        if 'id' not in session:
            return abort(401)
        seasonNumber = season
        series = stream.getSeries(series)
        season = stream.getSeason(series['seasons'][str(season)]['id'])
        if session['perms']['links'] == True:
            if request.method == 'POST':
                number = int(request.form['number'])
                language = request.form['language']
                link = request.form['link']
                hoster = request.form['hoster']
                name = request.form['name']
                description = request.form['description']
                season = season['id']
                seriesName = series['name']
                series = series['id']
                stream.createEpisode(season, language=language, link=link, hoster=hoster, number=number, name=name, description=description)
                subscribers = watch.getAllSubscribers(series)
                for subscriber in subscribers:
                    notifications.newNotification(subscriber, 5000, 0, 'subscribtion', f'New Episode {seriesName} Released', f'A <a href="/stream/{series}/{seasonNumber}/{number}">New Episode from {seriesName}</a> in {language} released. Watch it now!', 'info')
                return redirect(f'/stream/{series}/{seasonNumber}/{number}')
            else:
                return render_template('pages/stream/add_episode.html', session=session, info=info, series=series, season=season)
        else:
            return abort(403)
    elif episode.lower() == 'delete':
        if 'id' not in session: return abort(401)
        if session['perms']['links'] == True:
            episodeNumber = request.form['episode']
            seasonNumber = season
            stream.deleteStructuredEpisode(series, seasonNumber, episodeNumber)
            return 'deleted'
        else:
            return abort(403)
    seasonNumber = season
    episodeNumber = episode

    if str(series[0]) in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
        series = stream.getSeries(series)
    else:
        series = stream.getSeriesByName(series)
    
    seriesId = series['id']

    if str(season) not in series['seasons']: return redirect(f'/stream/{seriesId}')
    episodes = stream.getStructurEpisodes(seriesId, season, episode)
    if episodes == []: return redirect(f'/stream/{seriesId}/{season}')

    season = stream.getSeason(series['seasons'][str(season)]['id'])
    
    episodesUL = []
    aLLanguags = []

    for e in episodes:
        l = e['language']
        if l in aLLanguags:
            continue
        else:
            episodesUL.append(e)
            aLLanguags.append(l)


    if 'id' in session:
        watched = bool(watch.getEpisode(episodes[0]['id'], session['id']))
        watchedEpisodes = watch.getSeasonWatchedEpisodes(seriesId, seasonNumber, session['id'])
        subscribed = watch.isSubscribed(session['id'], series['id'])
    else:
        watched = False
        watchedEpisodes = []
        subscribed = False        
    seriesScore = stream.getTotalScore_Series(seriesId)
    return render_template('pages/stream/episode.html', info=info, session=session, episodes=episodes, seriesinfo=series, season=season, seasonNumber=seasonNumber, episodeNumber=episodeNumber, watched=watched, subscribed=subscribed, watchedEpisodes=watchedEpisodes, episodesUL=episodesUL, seriesScore=seriesScore)

# legal
@app.route('/dmca')
def dmca():
    return render_template('pages/legal/dmca.html', session=session, info=info)

# admin
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'id' not in session: abort(401)
    if session['perms']['admin'] != True: abort(403)
    if request.method == 'POST':
        if 'key' in request.form and 'value' in request.form:
            key = str(request.form['key']).lower()
            value = request.form['value']
            if key in ['language']:
                info['language'] = str(value)
                del info['defaultlanguage']
                with open('config.json', 'w') as f:
                    json.dump(info, f, indent=2)
                info['defaultlanguage'] = value
                info['language'] = lang
                return 'changed default language'
            else:
                return abort(400)
        else:
            return abort(400)
    else:
        return render_template('pages/admin/admin.html', info=info, session=session)

@app.route('/admin/data', methods=['GET', 'POST'])
def admin_data():
    if 'id' not in session: return abort(401)
    if session['perms']['admin'] != True: abort(403)
    return render_template('pages/admin/data.html', session=session, info=info)

@app.route('/admin/user', methods=['GET', 'POST'])
def admin_user():
    if 'id' not in session: return abort(401)
    if session['perms']['admin'] != True: return abort(403)
    if request.method == 'POST':
        return 'comming soon'
    else:
        if 'id' in request.args:
            id = int(request.args['id'])
        else:
            id = 1
        users = accounts.getAccountArea(id, id + 19)
        return render_template('pages/admin/user.html', info=info, session=session, users=users, id=id)

@app.route('/admin/user/add', methods=['GET', 'POST'])
def admin_user_add():
    if 'id' not in session: return abort(401)
    if session['perms']['admin'] != True: return abort(403)
    if request.method == 'POST':
        if 'pwd' not in request.form: return abort(400)
        if 'pwd-2' not in request.form: return abort(400)
        if 'username' not in request.form: return abort(400)
        if 'mail' not in request.form: return abort(400)
        username = request.form['username']
        mail = request.form['mail']
        pwd = request.form['pwd']
        pwd_2 = request.form['pwd-2']
        if pwd != pwd_2: return 'the passwords are not the same!'
        if len(pwd) < 8: return 'the password is to short!'
        password = pwd
        user = accounts.createUser(username, mail, password)
        if user == 'this mail/username is already taken': return 'username/mail already taken!'
        return redirect(f'/admin/user?id={user}')
    else:
        return render_template('pages/admin/add_user.html', info=info, session=session)

# login / logout / register
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if '2fa' in request.form:
            username = str(request.form['username'])
            pwd = str(request.form['pwd'])
            fa = str(request.form['2fa']).replace(' ', '')
            valid = accounts.checkUserLogin(username, pwd)
            if valid == False:
                return render_template('pages/logioregi/login.html', session=session, info=info, error=True)
            else:
                user = accounts.getUserByUsername(username)

                if user.verify not in ['true', 'True', True, 1, '', None]:
                    return render_template('pages/logioregi/login.html', session=session, info=info, vermail=True)

                totp = pyotp.TOTP(user.fa)
                facode = str(totp.now())
                if facode == fa:
                    set_user_session(user)

                    notifications.newNotification(user.id, 3000, 0, 'welcome', info['language']['notifications']['welcome'][session['language']]['title'],
                    info['language']['notifications']['welcome'][session['language']]['text'].replace("{name}", user.name), 'success', inbox=False)

                    return redirect('/home')
                else:
                    return render_template('pages/logioregi/login.html', session=session, info=info, error=True)
        else:
            uauth = str(request.form['user'])
            if '@' in uauth:
                mail = uauth
                username = None
            else:
                username = uauth
                mail = None
            pwd = str(request.form['pwd'])
            valid = accounts.checkUserLogin(uauth, pwd)
            if valid == False:
                return render_template('pages/logioregi/login.html', session=session, info=info, error=True)
            if mail != None:
                user = accounts.getUserByMail(mail)
            else:
                user = accounts.getUserByUsername(username)

            if user.verify not in ['true', 'True', True, 1, None]:
                return render_template('pages/logioregi/login.html', session=session, info=info, vermail=True)

            if str(user.fa) == '':
                set_user_session(user)

                notifications.newNotification(user.id, 3000, 0, 'welcome', info['language']['notifications']['welcome'][session['language']]['title'],
                info['language']['notifications']['welcome'][session['language']]['text'].replace("{name}", user.name), 'success', inbox=False)

                if 'redirect' in request.args:
                    rd = str(request.args['redirect'])
                    if not rd.startswith('/'):
                        rd = '/home'
                else:
                    rd = '/home'
                return redirect(rd)
            else:
                return render_template('pages/logioregi/2fa.html', username=user.username, pwd=pwd, info=info, session=session)
    else:
        if 'redirect' in request.args:
            rd = str(request.args['redirect'])
            if not rd.startswith('/'):
                rd = '/home'
        else:
            rd = '/home'
        return render_template('pages/logioregi/login.html', session=session, info=info, rd=rd)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if info['register'] == False: return abort(403)
    if request.method == 'POST':
        username = request.form['username']
        mail = request.form['mail']
        password = request.form['password']
        if accounts.isUsernameTaken(username):
            return render_template('pages/logioregi/register.html', info=info, session=session, usernametaken=True)
        elif accounts.isMailTaken(mail):
            return render_template('pages/logioregi/register.html', info=info, session=session, mailtaken=True)

        token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(256))
        userId = accounts.createUser(username, mail, password, verify=token)

        user = accounts.getUser(userId)
        pre_id = user.id

        send_verification_mail(token, mail, pre_id)
        return render_template('pages/logioregi/login.html', session=session, info=info, vermail=True)
    else:
        return render_template('pages/logioregi/register.html', info=info, session=session)

def set_user_session(user):
    session['mail'] = user.mail
    session['username'] = user.username
    session['id'] = user.id
    session['2fa'] = user.fa
    session['language'] = user.language
    session['description'] = user.description
    session['location'] = user.location
    session['birthday'] = user.birthday
    session['name'] = user.name
    session['theme'] = user.theme

    session['image'] = user.image
    session['banner'] = user.banner

    session['perms'] = {}
    session['perms']['admin'] = user.perms.admin
    session['perms']['links'] = user.perms.links

@app.route('/verify', methods=['GET'])
def verify():
    token = request.args['token']
    id = request.args['id']
    user = accounts.getUser(id)
    if str(user.verify) == token:
        accounts.updateVerify(id, 'True')
        return render_template('pages/logioregi/login.html', info=info, session=session, verified=True)
    else:
        return 'invalid token!!!'

def send_verification_mail(token, receiver, id):
    server = info['verification_mail_server']
    port = info['verification_mail_port']
    mail = info['verification_mail_mail']
    pwd = info['verification_mail_password']

    link = f'{info["domain"]}/verify?token={token}&id={id}'

    msg = EmailMessage()
    msg['Subject'] = f'Verification Mail - {info["name"]}'
    msg['From'] = mail
    msg['To'] = receiver
    msg.set_content(f'Please click on the link below to verify your email. {link}')

    msg.add_alternative(f"""\
        <!DOCTYPE html>
        <html>
            <body style="text-align: center;>
                <h1">Verification Mail - {info["name"]}</h1>
                <p>Please click on the Button below to verify your Mail.</p>
                <a href='{link}'><button style="margin: 5px; text-align: center; padding: 12px 20px; border: none; background-color: black; color: white; overflow: hidden; cursor: pointer; -webkit-appearance: none;">Verify Mail</button></a>
                <br><br><br><br>
                <span><a href="{link}">Click here if the button doesnt work</a></span>
            <body>
            <footer style="margin-top: 40vh;">
            <p>This Mail was auto sent by registering on {info["domain"]} - If it wasn't you please ignore the mail</p>
            </footer
        </html>
    """, subtype='html')

    with smtplib.SMTP(server, port) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login(mail, pwd)
        smtp.send_message(msg)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/home')

# Background POST Requests
## Notifications
@app.route('/get/notifications', methods=['POST'])
def get_notifications():
    if 'id' not in session: return {}
    nots = notifications.getUnreadUserNotifications(session['id'], True)
    notis = []
    for noti in nots:
        notis.append({
            "id": noti.id,
            "type": noti.type,
            "title": noti.title,
            "text": noti.text,
            "duration": noti.duration,
            "buttons": noti.buttons
        })
    return {"notifications": notis}

@app.route('/get/notifications_list', methods=['POST'])
def get_notifications_list():
    if 'id' not in session: return {}
    nots = notifications.getNewestNotifications(session['id'])
    notis = []
    for noti in nots:
        notis.append({
            "id": noti.id,
            "type": noti.type,
            "title": noti.title,
            "text": noti.text,
            "duration": noti.duration,
            "buttons": noti.buttons
        })
    return {"notifications": notis}

## Completed
@app.route('/background/set_completed_episode', methods=['POST'])
def background_set_completed_episode():
    if 'id' not in session: return abort(401)
    form = request.form
    if 'episode' not in form or 'series' not in form or 'episodeNumber' not in form or 'seasonNumber' not in form or 'seriesName' not in form: return abort(400)
    episode = int(form['episode'])
    series = int(form['series'])
    episodeNumber = int(form['episodeNumber'])
    seasonNumber = int(form['seasonNumber'])
    season = int(form['season'])
    seriesName = str(form['seriesName'])
    user = int(session['id'])
    watch.setCompleted(user, episode, series=series, episodeNumber=episodeNumber, seasonNumber=seasonNumber, seriesName=seriesName, season=season)
    return 'ok'

@app.route('/background/viewcountadd', methods=['POST'])
def background_viewcountadd():
    ip = str(request.remote_addr)
    seasonNumber = request.form['seasonNumber']
    series = request.form['series']
    episodeNumber = request.form['episodeNumber']
    r = stream.markAsWatchedRequest(series, seasonNumber, episodeNumber, ip)
    if r:
        return 'ok'
    else:
        return abort(429)

## Subscribe
@app.route('/background/subscribe_series', methods=['POST'])
def background_subscribe_series():
    if 'id' not in session: return abort(401)
    series = int(request.form['series'])
    watch.subscribeSeries(session['id'], series)
    return 'subscribed'

@app.route('/background/unsubscribe_series', methods=['POST'])
def background_unsubscribe_series():
    if 'id' not in session: return abort(401)
    series = int(request.form['series'])
    watch.unsubscribeSeries(session['id'], series)
    return 'unsubscribed'

@app.route('/background/del_completed_episode', methods=['POST'])
def background_del_completed_episode():
    if 'id' not in session: return abort(401)
    if session['perms']['links'] != True: return abort(403)
    form = request.form
    if 'episode' not in form: return abort(400)
    watch.delCompleted(session['id'], int(form['episode']))
    return 'ok'

@app.route('/background/del_stream', methods=['POST'])
def background_del_stream():
    if 'id' not in session: return abort(401)
    if session['perms']['links'] != True: return abort(403)
    streamId = int(request.form['stream'])
    stream.deleteEpisode(streamId)
    return 'ok'

# Social
@app.route('/discord')
def discord_redirect():
    return redirect(info['discord'])

# Sitemap
@app.route('/sitemap', methods=['GET', 'POST'])
@app.route('/sitemap.xml', methods=['GET', 'POST'])
def sitemap():
    seriesIndex = stream.getUnstructuredSeriesIndex()
    template = render_template('rsc/sitemap.xml', info=info, seriesIndex=seriesIndex)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'
    return response

# error handeling
## 400
@app.errorhandler(400)
def bad_request(error):
    return 'bad request'

@app.errorhandler(401)
def not_loged_in(error):
    return redirect('/login')

@app.errorhandler(403)
def not_allowed(error):
    return 'youre not allowed to access this resource'

@app.errorhandler(404)
def not_found(error):
    return render_template('pages/error/404.html', session=session, info=info)

## 500
@app.errorhandler(500)
def internal_server_error(error):
    return render_template('pages/error/500.html', session=session, info=info)


if __name__ == '__main__':
    app.run(debug=True, port=8080, host="127.0.0.1")
