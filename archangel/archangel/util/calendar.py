import sqlite3
import time

"""
releases (id int, creator int, created int, mod int, time int, seriesname text, description text, series int, season int, episode int, language int, image text);
"""

db = 'db/calendar.db'

def jsonfyRelease(releaseObject: tuple) -> dict:
    release = {
        "id": releaseObject[0],
        "creator": releaseObject[1],
        "created": releaseObject[2],
        "mod": releaseObject[3],
        "time": releaseObject[4],
        "seriesname": releaseObject[5],
        "description": releaseObject[6],
        "series": releaseObject[7],
        "season": releaseObject[8],
        "episode": releaseObject[9],
        "language": releaseObject[10],
        "image": releaseObject[11]
    }
    return release

def clearReleases():
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('DELETE FROM releases')
    conn.commit()
    conn.close()

def setRelease(creator: int, ts: int, seriesname: str, series: int, season: int, episode: int, language: str, image: str, description: str='', created: int=time.time()) -> int:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT MAX(id) FROM releases;')
    newid = c.fetchone()[0]
    if newid == None:
        newid = 1
    else:
        newid += 1
    c.execute('INSERT INTO releases VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (newid, creator, created, created, ts, seriesname, description, series, season, episode, language, image))
    conn.commit()
    conn.close()
    print(newid)

def getReleases(startts: int, endts: int) -> list:
    releases = []
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM releases WHERE time >= ? AND time <= ? ORDER BY time ASC;', (startts, endts))
    rls = c.fetchall()
    conn.close()
    for r in rls:
        rs = jsonfyRelease(r)
        releases.append(rs)
    return releases