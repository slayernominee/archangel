import sqlite3
import time
import hashlib

"""
seriesScores (id integer, series integer, score integer, voter integer, time integer);
seasonScores (id integer, season integer, score integer, voter integer, time integer);
episodeScores (id integer, episode integer, score integer, voter integer, time integer);

series (id int, name str, updated int, image str, banner str, description str, country str, stuff str, genres str, studio str, alternative str, startyear int, endyear int, age int, created int, subgenres str, publisher str, views int);
season (id int, series int, number int, name int, description str, views int);
episode (id int, series int, season integer, language str, name str, description str, number int, link str, hoster str, created int, views int);

views (ip text, time int, episode int); | Only for check that not to many requests

requests (id int, name str, requestor int, votes int, requested int, done int);
rvotes (id int, user int, voted int);
"""

db = 'db/stream.db'

streamlangsztoa = True

# Scoring
def newScoreId_Series() -> int:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT MAX(id) FROM seriesScores')
    maxid = c.fetchone()[0]
    conn.close()
    if maxid == None:
        return 1
    else:
        return maxid + 1
def newScoreId_Season() -> int:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT MAX(id) FROM seasonScores')
    maxid = c.fetchone()[0]
    conn.close()
    if maxid == None:
        return 1
    else:
        return maxid + 1
def newScoreId_Episode() -> int:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT MAX(id) FROM episodeScores')
    maxid = c.fetchone()[0]
    conn.close()
    if maxid == None:
        return 1
    else:
        return maxid + 1

def score_Series(score: int, series: int, voter: int) -> int:
    """Will create a new Entry or Update an existing Entry"""
    t = time.time()
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT id FROM seriesScores WHERE series=? AND voter=?', (series, voter))
    e = c.fetchone()
    if e in [None, (None,), (None)]:
        id = newScoreId_Series()
        c.execute('INSERT INTO seriesScores VALUES (?, ?, ?, ?, ?)', (id, series, score, voter, t))
    else:
        id = e[0]
        c.execute('UPDATE seriesScores SET score=? WHERE id=?', (score, id))
        c.execute('UPDATE seriesScores SET time=? WHERE id=?', (t, id))
    conn.commit()
    conn.close()
    return id

def score_Season(score: int, season: int, voter: int) -> int:
    """Will create a new Entry or Update an existing Entry"""
    t = time.time()
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT id FROM seasonScores WHERE season=? AND voter=?', (season, voter))
    e = c.fetchone()
    if e in [None, (None,), (None)]:
        id = newScoreId_Season()
        c.execute('INSERT INTO seasonScores VALUES (?, ?, ?, ?, ?)', (id, season, score, voter, t))
    else:
        id = e[0]
        c.execute('UPDATE seasonScores SET score=? WHERE id=?', (score, id))
        c.execute('UPDATE seasonScores SET time=? WHERE id=?', (t, id))
    conn.commit()
    conn.close()
    return id

def score_Episode(score: int, episode: int, voter: int) -> int:
    """Will create a new Entry or Update an existing Entry"""
    t = time.time()
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT id FROM episodeScores WHERE episode=? AND voter=?', (episode, voter))
    e = c.fetchone()
    if e in [None, (None,), (None)]:
        id = newScoreId_Episode()
        c.execute('INSERT INTO episodeScores VALUES (?, ?, ?, ?, ?)', (id, episode, score, voter, t))
    else:
        id = e[0]
        c.execute('UPDATE episodeScores SET score=? WHERE id=?', (score, id))
        c.execute('UPDATE episodeScores SET time=? WHERE id=?', (t, id))
    conn.commit()
    conn.close()
    return id

def getTotalScore_Series(series: int) -> dict:
    score = {
        "score": 0,
        "votes": 0
    }
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM seriesScores WHERE series=?', (series, ))
    vts = c.fetchall()
    conn.close()
    scs = []
    for vt in vts:
        sc = int(vt[2])
        scs.append(sc)
    score['votes'] = len(scs)
    if len(scs) == 0:
        score['score'] = 0
    else:
        score['score'] = round(sum(scs) / len(scs))
    return score

def getTotalScore_Season(season: int) -> dict:
    score = {
        "score": 0,
        "votes": 0
    }
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM seasonScores WHERE season=?', (season, ))
    vts = c.fetchall()
    conn.close()
    scs = []
    for vt in vts:
        sc = int(vt[2])
        scs.append(sc)
    score['votes'] = len(scs)
    if len(scs) == 0:
        score['score'] = 0
    else:
        score['score'] = round(sum(scs) / len(scs))
    return score

def getTotalScore_Episode(episode: int) -> dict:
    score = {
        "score": 0,
        "votes": 0
    }
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM episodeScores WHERE episode=?', (episode, ))
    vts = c.fetchall()
    conn.close()
    scs = []
    for vt in vts:
        sc = int(vt[2])
        scs.append(sc)
    score['votes'] = len(scs)
    if len(scs) == 0:
        score['score'] = 0
    else:
        score['score'] = round(sum(scs) / len(scs))
    return score

# Episode
def newEpisodeId() -> int:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT MAX(id) FROM episode')
    maxid = c.fetchone()[0]
    conn.close()
    if maxid == None:
        return 1
    else:
        return maxid + 1

def newEpisodeNumber(season: int) -> int:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT MAX(number) FROM episode WHERE season=?', (season, ))
    maxid = c.fetchone()[0]
    conn.close()
    if maxid == None:
        return 1
    else:
        return maxid + 1

def getSeasonByEpisode(episode: int) -> int:
    # TODO!
    pass

def createEpisode(season: int, language: str, link: str, hoster: str, number: int=-1, name: str='', description: str='') -> int:
    """The season must exists!"""
    if number == -1:
        number = newEpisodeNumber(season)
    episode = newEpisodeId()
    series = getSeriesBySeason(season)
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('INSERT INTO episode VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (episode, series, season, language, name, description, number, link, hoster, time.time(), 0))
    conn.commit()
    conn.close()
    return episode

def getEpisode(episode: int):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM episode WHERE id=?', (episode,))
    episode = c.fetchone()
    conn.close()
    e = jsonfyEpisode(episode)
    return e

def getEpisodeLanguages(episode: int) -> list:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM episode WHERE id=?', (episode, ))
    episodes = c.fetchall()
    conn.commit()
    conn.close()
    epi = []
    for e in episodes:
        epi.append(e[3])
    return epi

def deleteEpisode(episode: int) -> None:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('DELETE FROM episode WHERE id=?', (episode, ))
    conn.commit()
    conn.close()

def jsonfyEpisode(episode: tuple, season: tuple=None, series: tuple=None) -> dict:
    e = {
        "id": episode[0],
        "series": episode[1],
        "season": episode[2],
        "language": episode[3],
        "name": episode[4],
        "description": episode[5],
        "number": episode[6],
        "link": episode[7],
        "hoster": episode[8],
        "created": episode[9]
    }
    if season:
        e['seasonNumber'] = season[2]
    else:
        e['seasonNumber'] = '<deleted>'
    if series:
        e['seriesName'] = series[1]
    else:
        e['seriesName'] = '<deleted>'
    return e

# Season
def newSeasonId() -> int:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT MAX(id) FROM season')
    maxid = c.fetchone()[0]
    conn.close()
    if maxid == None:
        return 1
    else:
        return maxid + 1

def newSeasonNumber(series: int) -> int:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT MAX(number) FROM season WHERE series=?', (series, ))
    maxid = c.fetchone()[0]
    conn.close()
    if maxid == None:
        return 1
    else:
        return maxid + 1

def getSeriesBySeason(season: int) -> int:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT series FROM season WHERE id=?', (season, ))
    series = c.fetchone()
    conn.close()
    return series[0]

def createSeason(series: int, number: int=-1, name: str='', description: str='') -> int:
    """The series must exists"""
    if number == -1:
        number = newSeasonNumber(series)
    season = newSeasonId()
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('INSERT INTO season VALUES (?, ?, ?, ?, ?, ?)', (season, series, number, name, description, 0))
    conn.commit()
    conn.close()
    return season

def getSeason(season: int):
    seasonId = season
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM season WHERE id=?', (season, ))
    season = c.fetchone()
    c.execute('SELECT * FROM episode WHERE season=? ORDER BY number ASC', (seasonId, ))
    episodes = c.fetchall()
    conn.close()
    s = {
        "id": season[0],
        "series": season[1],
        "number": season[2],
        "name": season[3],
        "description": season[4],
        "episodes": {}
    }
    for e in episodes:
        ep = jsonfyEpisode(e)
        if str(e[6]) in s['episodes']:
            s['episodes'][str(e[6])].append(ep)
        else:
            s['episodes'][str(e[6])] = [ep]

    return s

# Series
def jsonfySeries(seriesObject: tuple, seasonObjects: list=[]) -> dict:
    if seriesObject in [None, (None)]: return None
    genres = seriesObject[8]
    stuff = seriesObject[7]
    alternative = seriesObject[10]
    subgenres = seriesObject[15]
    seasons = {}
    
    for season in seasonObjects:
        seasons[str(season[2])] = {
            "id": season[0],
            "series": season[1],
            "number": season[2],
            "name": season[3],
            "description": season[4]
        }
    sorted_seasons = {}
    for s in sorted(seasons):
        sorted_seasons[s] = seasons[s]
    seasons = sorted_seasons
    seriesinfo = {
        "id": seriesObject[0],
        "name": seriesObject[1],
        "image": seriesObject[3],
        "banner": seriesObject[4],
        "description": seriesObject[5],
        "country": seriesObject[6],
        "stuff": [],
        "genres": [],
        "studio": seriesObject[9],
        "alternative": [],
        "seasons": seasons,
        "startyear": seriesObject[11],
        "endyear": seriesObject[12],
        "age": seriesObject[13],
        "created": seriesObject[14],
        "subgenres": []
    }
    if genres != None:
        for g in genres.split(","):
            if g == '': continue
            seriesinfo['genres'].append(g)

    if stuff != None:
        for g in stuff.split(","):
            if g == '': continue
            seriesinfo['stuff'].append(g)

    if alternative != None:
        for g in alternative.split(","):
            if g == '': continue
            seriesinfo['alternative'].append(g)

    if subgenres != None:
        for g in subgenres.split(","):
            if g == '': continue
            seriesinfo['subgenres'].append(g)

    return seriesinfo

def newSeriesId() -> int:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT MAX(id) FROM series')
    maxid = c.fetchone()[0]
    conn.close()
    if maxid == None:
        return 1
    else:
        return maxid + 1

def createSeries(name, updated: int=time.time(), image: str='', banner: str='', description: str='', country: str='', stuff: list=[], genres: list=[], subgenres: list=[], studio: str='', alternativ: list=[], age: int=-1, startyear: int=-1, endyear: int=-1) -> int:
    series = newSeriesId()
    conn = sqlite3.connect(db)
    c = conn.cursor()
    genre = ''
    for g in genres:
        genre += g + ','
    
    subgenre = ''
    for g in subgenres:
        subgenre += g + ','
    
    staff = ''
    for s in stuff:
        staff += s + ','
    alternative = ''
    for al in alternativ:
        alternative += al + ','
    c.execute('INSERT INTO series VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (series, name, updated, image, banner, description, country, ',' + staff, ',' + genre, studio, ',' + alternative, startyear, endyear, age, updated, ',' + subgenre, 0))
    conn.commit()
    conn.close()
    return series

def getSeries(series: int) -> dict:
    seriesId = series
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM series WHERE id=?', (series, ))
    series = c.fetchone()
    c.execute('SELECT * FROM season WHERE series=? ORDER BY number ASC', (seriesId, ))
    seasons = c.fetchall()
    conn.close()
    series = jsonfySeries(series, seasons)
    return series

def getManySeries(series: list) -> list:
    se = []
    conn = sqlite3.connect(db)
    c = conn.cursor()
    for s in series:
        c.execute('SELECT * FROM series WHERE id=?', (s, ))
        serie = c.fetchone()
        c.execute('SELECT * FROM season WHERE series=? ORDER BY number ASC', (s, ))
        seasons = c.fetchall()
        serieJ = jsonfySeries(serie, seasons)
        se.append(serieJ)
    return se

def getSeriesIndex() -> dict:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM series')
    series = c.fetchall()
    conn.close()
    se = {
    "a": [], "b": [], "c": [], "d": [], "e": [], "f": [], "g": [], "h": [], "i": [],
    "j": [], "k": [], "l": [], "m": [], "n": [], "o": [], "p": [], "q": [], "r": [],
    "s": [], "t": [], "u": [], "v": [], "w": [], "x": [], "y": [], "z": [], "#": []
    }
    for s in series:  
        if str(s[1])[0].lower() in se:
            se[str(s[1])[0].lower()].append({
                "id": s[0],
                "name": s[1],

                "image": s[3],
                "banner": s[4]
            })
        else:
            se['#'].append({
                "id": s[0],
                "name": s[1],

                "image": s[3],
                "banner": s[4]
            })

    return se

def getSeriesIndex_Genre() -> dict:
    sl = []
    sg = []
    se = {}
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM series')
    series = c.fetchall()

    conn.close()
    for s in series:  
        sx = jsonfySeries(s)
        sl.append(se)
        for genre in sx['genres']:
            if genre not in se:
                se[genre] = [sx]
            else:
                se[genre].append(sx)

    se_s = {}
    for genre in sorted(se):
        se_s[genre] = se[genre]

    return se_s

def getSeriesIndex_StartYear() -> dict:
    sl = []
    sg = []
    se = {}
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM series')
    series = c.fetchall()

    conn.close()
    for s in series:  
        sx = jsonfySeries(s)
        sl.append(se)
        if str(sx['startyear']) not in se:
            se[str(sx['startyear'])] = [sx]
        else:
            se[str(sx['startyear'])].append(sx)

    se_s = {}
    for genre in sorted(se):
        se_s[genre] = se[genre]

    return se_s

def getRandomSeriesId() -> int:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT id FROM series ORDER BY random() LIMIT 1')
    id = c.fetchone()
    return id[0]

def getUnstructuredSeriesIndex() -> list:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM series')
    series = c.fetchall()
    se = []
    for s in series:
        c.execute('SELECT * FROM season WHERE series=?', (s[0],))
        seasons = c.fetchall()
        se.append(jsonfySeries(s, seasons))
    conn.close()
    return se

def getSeriesByName(seriesName: str) -> dict:
    if seriesName[0] in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
        seriesName = '-' + seriesName
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM series WHERE name=?', (seriesName, ))
    series = c.fetchone()
    c.execute('SELECT * FROM season WHERE series=?', (series[0], ))
    seasons = c.fetchall()
    conn.close()
    series = jsonfySeries(series, seasons)
    return series

def getSeriesWithGenre(genre: str) -> list:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM series WHERE genres LIKE ?', ('%,' + genre + ',%',))
    series = c.fetchall()
    conn.close()
    se = []
    for s in series:
        se.append(jsonfySeries(s))
    return se

def getSeriesWithStudio(studio: str) -> list:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM series WHERE studio=?', (studio,))
    series = c.fetchall()
    conn.close()
    se = []
    for s in series:
        se.append(jsonfySeries(s))
    return se

def getSeriesWithStaff(genre: str) -> list:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM series WHERE stuff LIKE ?', ('%,' + genre + ',%',))
    series = c.fetchall()
    conn.close()
    se = []
    for s in series:
        se.append(jsonfySeries(s))
    return se

def getSeriesWithAge(age: int) -> list:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM series WHERE age=?', (age,))
    series = c.fetchall()
    conn.close()
    se = []
    for s in series:
        se.append(jsonfySeries(s))
    return se

def getSeriesWithSubGenre(genre: str) -> list:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM series WHERE subgenres LIKE ?', ('%,' + genre + ',%',))
    series = c.fetchall()
    conn.close()
    se = []
    for s in series:
        se.append(jsonfySeries(s))
    return se

def getSeriesWithCountry(country: str) -> list:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM series WHERE LOWER(country)=?', (country.lower(),))
    series = c.fetchall()
    conn.close()
    se = []
    for s in series:
        se.append(jsonfySeries(s))
    return se

def searchSeries(query: str) -> list:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM series WHERE LOWER(name) LIKE ? OR LOWER(alternative) LIKE ?', ('%' + query.lower() + '%', '%' + query.lower() + '%'))
    result = c.fetchall()
    conn.close()
    results = []
    for r in result:
        staff = []
        staf = r[7]
        if staf != None:
            for s in staf.split(","):
                if s == '': continue
                staff.append(s)
        
        genres = []
        genre = r[8]
        if genre != None:
            for s in genre.split(","):
                if s == '': continue
                genres.append(s)

        alternative = []
        alternativ = r[10]
        if alternativ != None:
            for s in alternativ.split(","):
                if s == '': continue
                alternative.append(s)

        results.append({
            "id": r[0],
            "name": r[1],
            "image": r[3],
            "banner": r[4],
            "description": r[5],
            "country": r[6],
            "staff": staff,
            "genres": genres,
            "studio": r[9],
            "alternative": alternative
        })
    return results
    
def deleteSeries(id: int) -> None:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('DELETE FROM series WHERE id=?', (id, ))
    c.execute('DELETE FROM season WHERE series=?', (id, ))
    c.execute('DELETE FROM episode WHERE series=?', (id, ))
    conn.commit()
    conn.close()

## Update
def seriesUpdateName(id: int, name: str) -> None:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('UPDATE series SET name=? WHERE id=?', (name, id))
    conn.commit()
    conn.close()

def seriesUpdateDescription(id: int, description: str) -> None:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('UPDATE series SET description=? WHERE id=?', (description, id))
    conn.commit()
    conn.close()

def seriesUpdateStartYear(id: int, year: int) -> None:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('UPDATE series SET startyear=? WHERE id=?', (year, id))
    conn.commit()
    conn.close()

def seriesUpdateEndYear(id: int, year: int) -> None:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('UPDATE series SET endyear=? WHERE id=?', (year, id))
    conn.commit()
    conn.close()

def seriesUpdateImage(id: int, image: str) -> None:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('UPDATE series SET image=? WHERE id=?', (image, id))
    conn.commit()
    conn.close()

def seriesUpdateBanner(id: int, banner: str) -> None:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('UPDATE series SET banner=? WHERE id=?', (banner, id))
    conn.commit()
    conn.close()

def seriesUpdateCountry(id: int, country: str) -> None:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('UPDATE series SET country=? WHERE id=?', (country, id))
    conn.commit()
    conn.close()

def seriesUpdateStudio(id: int, studio: str) -> None:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('UPDATE series SET studio=? WHERE id=?', (studio, id))
    conn.commit()
    conn.close()

def seriesUpdateGenres(id: int, genres: list) -> None:
    genre_str = ','
    for genre in genres:
        genre_str += genre + ','
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('UPDATE series SET genres=? WHERE id=?', (genre_str, id))
    conn.commit()
    conn.close()

def seriesUpdateStaff(id: int, staff: list) -> None:
    staff_str = ','
    for sta in staff:
        staff_str += sta + ','
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('UPDATE series SET stuff=? WHERE id=?', (staff_str, id))
    conn.commit()
    conn.close()

def seriesUpdateSubgenres(id: int, genres: list) -> None:
    genre_str = ','
    for genre in genres:
        genre_str += genre + ','
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('UPDATE series SET subgenres=? WHERE id=?', (genre_str, id))
    conn.commit()
    conn.close()

def seriesUpdateAlternative(id: int, alternative: list) -> None:
    alternative_str = ','
    for alternativ in alternative:
        alternative_str += alternativ + ','
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('UPDATE series SET alternative=? WHERE id=?', (alternative_str, id))
    conn.commit()
    conn.close()

def seriesUpdateAge(id: int, age: int) -> None:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('UPDATE series SET age=? WHERE id=?', (age, id))
    conn.commit()
    conn.close()

# Requests
def newRequestId() -> int:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT MAX(id) FROM requests')
    maxid = c.fetchone()[0]
    conn.close()
    if maxid == None:
        return 1
    else:
        return maxid + 1

def createNewRequest(name: str, requestor: int) -> int:
    requested = time.time()
    id = newRequestId()
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('INSERT INTO requests VALUES (?, ?, ?, ?, ?, ?)', (id, name, requestor, 0, requested, False))
    conn.commit()
    conn.close()
    return id

def disableRequest(request: int) -> None:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('UPDATE requests SET done=? WHERE id=?', (True, request))
    conn.commit()
    conn.close()

def jsonfyRequests(requestObject: tuple):
    request = {
        "id": requestObject[0],
        "name": requestObject[1],
        "requestor": requestObject[2],
        "votes": requestObject[3],
        "requested": requestObject[4],
        "done": bool(requestObject[5])
    }
    return request

def getRequests(count: int=None) -> list:
    reqs = []
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM requests WHERE done=0 ORDER BY votes DESC')
    if count == None:
        rq = c.fetchall()
    else:
        rq = c.fetchmany(size=count)
    conn.close()
    for r in rq:
        rJ = jsonfyRequests(r)
        reqs.append(rJ)
    return reqs

def voteUpRequest(req: int, user: int):
    date = time.time()
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM rvotes WHERE id=? AND user=?', (req, user))
    check = c.fetchone()
    if check in [None, (None,), [None]]:
        c.execute('INSERT INTO rvotes VALUES (?, ?, ?)', (req, user, date))
        c.execute('UPDATE requests SET votes=votes + 1 WHERE id=?', (req,))
        conn.commit()
        conn.close()
    else:
        conn.close()

def voteDownRequest(req: int, user: int):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM rvotes WHERE id=? AND user=?', (req, user))
    check = c.fetchone()
    if check in [None, (None,), [None]]:
        conn.close()
    else:
        c.execute('DELETE FROM rvotes WHERE id=? AND user=?', (req, user))
        c.execute('UPDATE requests SET votes=votes - 1 WHERE id=?', (req,))
        conn.commit()
        conn.close()

def getUserRequestVotes(user: int) -> list:
    votes = []
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM rvotes WHERE user=?', (user, ))
    uvotes = c.fetchall()
    conn.close()
    for vote in uvotes:
        votes.append(vote[0])
    return votes

# Misc
def getStructurEpisodes(series: int, seasonNumber: int, episodeNumber: int) -> int:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT id FROM season WHERE series=? AND number=?', (series, seasonNumber))
    season = c.fetchone()
    if season in [None, (None)]:
        conn.close()
        return None
    else:
        season = season[0]
    if streamlangsztoa:
        c.execute('SELECT * FROM episode WHERE series=? AND season=? AND number=? ORDER BY language DESC', (series, season, episodeNumber))
    else:
        c.execute('SELECT * FROM episode WHERE series=? AND season=? AND number=? ORDER BY language ASC', (series, season, episodeNumber))
    episodes = c.fetchall()
    conn.close()
    epis = []
    for episode in episodes:
        e = getEpisode(episode[0])
        epis.append(e)
    return epis

def markAsWatchedRequest(series: int, seasonNumber: int, episodeNumber: int, ip: str):
    """This will write a new view, if the ip doesnt have sent a request in the last 5 minutes (this is for not botting etc) | ip addresses will be saved as hashes and deleted after 10minutes + a new request"""
    ip = hashlib.sha512(bytes(ip, 'utf-8')).hexdigest()
    now = time.time()
    now_m_5 = time.time() - (60 * 5)
    now_m_10 = time.time() - (60 * 10)
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM views WHERE ip=? AND time>?', (ip, now_m_5))
    e = c.fetchone()
    if e in [None, (None,), (None)]:
        c.execute('DELETE FROM views WHERE time<?', (now_m_10, ))
        c.execute('INSERT INTO views VALUES (?, ?, ?)', (ip, now, 0))
        conn.commit()
        allow = True
    else:
        allow = False
    conn.close()
    if allow:
        markStructuredEpisodeAsWatched(series, seasonNumber, episodeNumber)
        return True
    else:
        return False

def markStructuredEpisodeAsWatched(series: int, seasonNumber: int, episodeNumber: int):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT views FROM series WHERE id=?', (series, ))
    views = c.fetchone()[0]
    if views == None: views = 0
    views += 1
    c.execute('UPDATE series SET views=? WHERE id=?', (views, series))
    
    c.execute('SELECT id FROM season WHERE series=? AND number=?', (series, seasonNumber))
    season = c.fetchone()[0]
    c.execute('SELECT views FROM season WHERE series=? AND number=?', (series, seasonNumber))
    views = c.fetchone()[0]
    if views == None: views = 0
    views += 1
    c.execute('UPDATE season SET views=? WHERE id=?', (views, season))
    
    c.execute('SELECT views FROM episode WHERE series=? AND season=? AND number=?', (series, season, episodeNumber))
    views = c.fetchone()[0]
    if views == None: views = 0
    views += 1
    c.execute('UPDATE episode SET views=? WHERE series=? AND season=? AND number=?', (views, series, season, episodeNumber))
    print(views)

    conn.commit()
    conn.close()


def deleteStructuredSeason(series: int, seasonNumber: int) -> None:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT id FROM season WHERE series=? AND number=?', (series, seasonNumber))
    season = c.fetchone()[0]
    c.execute('DELETE FROM season WHERE id=?', (season, ))
    c.execute('DELETE FROM episode WHERE season=? AND series=?', (season, series))
    conn.commit()
    conn.close()

def deleteStructuredEpisode(series, seasonNumber, episodeNumber) -> None:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT id FROM season WHERE series=? AND number=?', (series, seasonNumber))
    season = c.fetchone()[0]
    c.execute('DELETE FROM episode WHERE series=? AND number=? AND season=?', (series, episodeNumber, season))
    conn.commit()
    conn.close()

def getGenreIndex() -> list:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT genres FROM series')
    allgenreentrys = c.fetchall()
    conn.commit()
    conn.close()
    genres = []
    for genreentry in allgenreentrys:
        genrestring = genreentry[0]
        for genre in genrestring.split(","):
            if genre == '': continue
            if genre in genres: continue
            genres.append(genre)
    return genres

def getSubGenreIndex() -> list:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT subgenres FROM series')
    allgenreentrys = c.fetchall()
    conn.commit()
    conn.close()
    genres = []
    for genreentry in allgenreentrys:
        genrestring = genreentry[0]
        for genre in genrestring.split(","):
            if genre == '': continue
            if genre in genres: continue
            genres.append(genre)
    return genres

def getNewestCreatedSeries(count: int=15) -> list:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM series WHERE created!="" ORDER BY created DESC')
    series = c.fetchmany(size=count)
    conn.close()
    se = []
    for serie in series:
        if serie in [None]: continue
        genres = serie[8]
        stuff = serie[7]
        alternative = serie[10]

        seriesinfo = {
            "id": serie[0],
            "name": serie[1],
            "image": serie[3],
            "banner": serie[4],
            "description": serie[5],
            "country": serie[6],
            "stuff": [],
            "genres": [],
            "studio": serie[9],
            "alternative": [],
            "seasons": [],
            "startyear": serie[11],
            "endyear": serie[12],
            "age": serie[13],
            "created": serie[14]
        }
        if genres != None:
            for g in genres.split(","):
                if g == '': continue
                seriesinfo['genres'].append(g)

        if stuff != None:
            for g in stuff.split(","):
                if g == '': continue
                seriesinfo['stuff'].append(g)

        if alternative != None:
            for g in alternative.split(","):
                if g == '': continue
                seriesinfo['alternative'].append(g)
        se.append(seriesinfo)
    return se

def getNewestCreatedEpisodes(count: int=32) -> list:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM episode WHERE created!="" ORDER BY created DESC')
    episodes = c.fetchmany(size=count)
    eps = []
    for episode in episodes:
        c.execute('SELECT * FROM season WHERE id=?', (episode[2], ))
        season = c.fetchone()
        c.execute('SELECT * FROM series WHERE id=?', (episode[1],))
        series = c.fetchone()
        if episode in [None, '', (None,)]: continue
        e = jsonfyEpisode(episode, season, series)
        eps.append(e)
    conn.close()
    return eps