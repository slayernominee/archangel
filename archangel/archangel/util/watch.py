import sqlite3
import time

"""
completed (series:int, season:int, seriesName text, seasonNumber:int, episodeNumber:int, episodeName text, date:int, user:int, episode: int);
abos (user: int, series: int, subscribed: int);
watchlistSeries (series:int, seriesName text, date:int, user:int);
"""

db = 'db/watch.db'

# completed
def setCompleted(user: int, episode:int, seasonNumber: int=None, episodeNumber: int=None, series: int=None, season: int=None, seriesName: str=None, episodeName: str=None) -> None:
    date = time.time()
    if episodeName == None: episodeName = str(episodeNumber)
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM completed WHERE user=? AND episode=?', (user, episode))
    e = c.fetchone()
    if e in [None, (None,), (None)]:
        c.execute('INSERT INTO completed VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)', (series, season, seriesName, seasonNumber, episodeNumber, episodeName, date, user, episode))
        conn.commit()
        conn.close()
    else:
        conn.close()

def delCompleted(user: int, episode: int) -> None:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('DELETE FROM completed WHERE user=? AND episode=?', (user, episode))
    conn.commit()
    conn.close()

def getEpisode(episode: int, user: int) -> dict:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM completed WHERE user=? AND episode=?', (user, episode))
    episodeElement = c.fetchone()
    conn.close()
    episode = jsonfyEpisode(episodeElement)
    return episode

def getSeasonWatchedEpisodes(series: int, seasonNumber: int, user: int) -> list:
    """Get The Watched Episodes Numbers from a Season | the elements will be strings"""
    watched = []
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM completed WHERE user=? AND series=? AND seasonNumber=?', (user, series, seasonNumber))
    wE = c.fetchall()
    conn.close()
    for w in wE:
        watched.append(str(w[4]))
    return sorted(watched)

def jsonfyEpisode(episodeElement: tuple) -> dict:
    if episodeElement in [None, (None,)]: return None
    episode = {
        'date': episodeElement[6],
        'user': episodeElement[7],
        'episode': episodeElement[8],

        'season': episodeElement[1],
        'series': episodeElement[0],
        'episodeName': episodeElement[5],
        'seriesName': episodeElement[2],
        'episodeNumber': episodeElement[4],
        'seasonNumber': episodeElement[3]
    }
    return episode

# abos
def subscribeSeries(user: int, series: int) -> None:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT user FROM abos WHERE user=? AND series=?', (user, series))
    e = c.fetchone()
    if e in [None, (None,), (None), [None]]:
        c.execute('INSERT INTO abos VALUES (?, ?, ?)', (user, series, time.time()))
        conn.commit()
        conn.close()
    else:
        conn.close()

def unsubscribeSeries(user: int, series: int) -> None:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('DELETE FROM abos WHERE user=? AND series=?', (user, series))
    conn.commit()
    conn.close()

def isSubscribed(user: int, series: int) -> bool:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT user FROM abos WHERE user=? AND series=?', (user, series))
    e = c.fetchone()
    conn.close()
    if e in [None, (None,), (None), [None]]:
        return False
    else:
        return True

def getAllSubscribers(series: int) -> list:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT user FROM abos WHERE series=?', (series, ))
    user = c.fetchall()
    conn.close()
    users = []
    for u in user:
        users.append(u[0])
    return users

def getAllSubscribedSeries(user: int) -> list:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM abos WHERE user=?', (user, ))
    series = c.fetchall()
    conn.close()
    se = []
    for serie in series:
        se.append(serie[1])
    return se