# copyright by Marcel Rieger

from flask import Flask, abort, redirect, render_template, send_file, session, request
import json
import os
import pyotp
import datetime
import random

from blue.rsc import rsc

from util import accounts, stream, notifications, watch

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
    seriesIndex = stream.getSeriesIndex()
    genreIndex = stream.getGenreIndex()
    newestCreated = stream.getNewestCreatedSeries(count=15)
    newestCreatedEpisodes = stream.getNewestCreatedEpisodes(count=20)
    return render_template('pages/home.html', info=info, session=session, seriesIndex=seriesIndex, spotlight=spotlight, genreIndex=genreIndex, newestCreated=newestCreated, newestCreatedEpisodes=newestCreatedEpisodes)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['query']
        results = stream.searchSeries(query)
        result = ''
        for r in results:
            result += f"""<a href="/stream/{r['id']}" style="text-decoration: none;">
        <div class=\"lent\""""
            if r['banner'].startswith('http'):
                result += f""" style="background: linear-gradient(rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.3)),url('{r['banner']}');\""""
            result += f"><img src=\"{r['image']}\">"
            if r['name'].startswith("-") and r["name"][1] in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                result += f"<h2>{r['name'][1:]}</h2>"
            else:
                result += f"<h2>{r['name']}</h2>"
            result += f"<span>{r['description'][:200]}</span>"
            result += '<div style="float: right;">'
            for genre in range(len(r['genres'])):
                if genre > 7:
                    result += f"<a href=\"/genre/{r['genres'][genre]}\">"
                    result += f"""<li class="tag" style="display: none;" id="{r['id']}-{genre}">
                        {r['genres'][genre]}</li></a>"""
                else:
                    result += f"<a href=\"/genre/{r['genres'][genre]}\"><li class=\"tag\" id=\"{r['id']}-{genre}\">{r['genres'][genre]}</li></a>"
            
            if len(r['genres']) > 7:
                result += f"""<li class="tag" id="{r['id']}-showall" onclick=\""""
                for id in range(len(r['genres'])):
                    result += f"""document.getElementById('{r['id']}-{id}').style.display = 'block';"""

                result += f"""document.getElementById('{r['id']}-showall').style.display = 'none';">
                    &{len(r['genres']) - 8} more
                </li>"""
            result += '</div></div></a>'

        return result
    else:
        return render_template('pages/search.html', info=info, session=session, seriesIndex=str(stream.getUnstructuredSeriesIndex()))

# Index
@app.route('/index', methods=['GET'])
def index():
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

@app.route('/subgenre/<genre>')
def subgenre(genre: str):
    series = stream.getSeriesWithSubGenre(genre)
    return render_template('pages/genre.html', info=info, session=session, genre=genre, series=series)

@app.route('/staff/<staff>')
def staff(staff: str):
    series = stream.getSeriesWithStaff(staff)
    return render_template('pages/genre.html', info=info, session=session, genre=staff, series=series)

@app.route('/notifications')
def notification_page():
    if 'id' not in session: return abort(401)
    return render_template('pages/notifications.html', info=info, session=session)

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
def account_subscribed():
    if 'id' not in session: return abort(401)
    subscribed_series = watch.getAllSubscribedSeries(session['id'])
    subscribed_series = stream.getManySeries(subscribed_series)

    return render_template('pages/account/subscribed.html', session=session, info=info, series=subscribed_series)

# streaming
@app.route('/stream/<seriesId>', methods=['GET', 'POST'])
def stream_series(seriesId):
    if info['public'] == False and 'id' not in session: return abort(401)
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
            genres = request.form['genres'].split(',')
            subgenres = request.form['subgenres'].split(',')
            alternative = request.form['alternative'].split(',')

            if name[0] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']: name = '-' + name

            if name != series['name']: stream.seriesUpdateName(seriesId, name)
            if description != series['description']: stream.seriesUpdateDescription(seriesId, description)
            if image != series['image']: stream.seriesUpdateImage(seriesId, image)
            if banner != series['banner']: stream.seriesUpdateBanner(seriesId, banner)
            if country != series['country']: stream.seriesUpdateCountry(seriesId, country)
            if studio != series['studio']: stream.seriesUpdateStudio(seriesId, studio)
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
        if str(seriesId[0]) in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
            series = stream.getSeries(seriesId)
        else:
            series = stream.getSeriesByName(seriesId)
        if series == None: abort(404)
        if 'id' in session:
            subscribed = watch.isSubscribed(session['id'], series['id'])
        else:
            subscribed = False
        return render_template('pages/stream/series.html', info=info, session=session, seriesinfo=series, subscribed=subscribed)

@app.route('/stream/<series>/<season>', methods=['GET', 'POST'])
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

    if str(seriesId[0]) in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
        series = stream.getSeries(seriesId)
    else:
        series = stream.getSeriesByName(seriesId)
    if str(season) not in series['seasons']: return abort(404)
    season = stream.getSeason(series['seasons'][str(season)]['id'])

    if 'id' in session:
        subscribed = watch.isSubscribed(session['id'], series['id'])
    else:
        subscribed = False

    return render_template('pages/stream/season.html', info=info, session=session, seriesinfo=series, season=season, seasonNumber=seasonNumber, subscribed=subscribed)

@app.route('/stream/<series>/<season>/<episode>', methods=['GET', 'POST'])
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
    if 'id' in session:
        watched = bool(watch.getEpisode(episodes[0]['id'], session['id']))
    else:
        watched = False
    if 'id' in session:
        subscribed = watch.isSubscribed(session['id'], series['id'])
    else:
        subscribed = False
    return render_template('pages/stream/episode.html', info=info, session=session, episodes=episodes, seriesinfo=series, season=season, seasonNumber=seasonNumber, episodeNumber=episodeNumber, watched=watched, subscribed=subscribed)

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
                totp = pyotp.TOTP(user.fa)
                facode = str(totp.now())
                if facode == fa:
                    session['mail'] = user.mail
                    session['username'] = user.username
                    session['id'] = user.id
                    session['2fa'] = user.fa
                    session['language'] = user.language
                    session['description'] = user.description
                    session['location'] = user.location
                    session['birthday'] = user.birthday
                    session['name'] = user.name

                    session['image'] = user.image
                    session['banner'] = user.banner

                    session['perms'] = {}
                    session['perms']['admin'] = user.perms.admin
                    session['perms']['links'] = user.perms.links

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

            if str(user.fa) == '':
                session['mail'] = user.mail
                session['username'] = user.username
                session['id'] = user.id
                session['2fa'] = user.fa
                session['language'] = user.language
                session['description'] = user.description
                session['location'] = user.location
                session['birthday'] = user.birthday
                session['name'] = user.name

                session['image'] = user.image
                session['banner'] = user.banner

                session['perms'] = {}
                session['perms']['admin'] = user.perms.admin
                session['perms']['links'] = user.perms.links

                notifications.newNotification(user.id, 3000, 0, 'welcome', info['language']['notifications']['welcome'][session['language']]['title'],
                info['language']['notifications']['welcome'][session['language']]['text'].replace("{name}", user.name), 'success', inbox=False)

                return redirect('/home')
            else:
                return render_template('pages/logioregi/2fa.html', username=user.username, pwd=pwd, info=info, session=session)
    else:
        return render_template('pages/logioregi/login.html', session=session, info=info)

@app.route('/register')
def register():
    return render_template('pages/logioregi/register.html', info=info, session=session)

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
    seriesName = str(form['seriesName'])
    user = int(session['id'])
    watch.setCompleted(user, episode, series=series, episodeNumber=episodeNumber, seasonNumber=seasonNumber, seriesName=seriesName)
    return 'ok'
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