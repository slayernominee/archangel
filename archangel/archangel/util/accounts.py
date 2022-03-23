import sqlite3
import hashlib

import os
import json
import time

'''
user (id integer, mail text, username text, name text, password text, birthday integer, location text, discord text, description text, website text, image text, banner text, verification text, twofa text, genres text, flairs text, favorites text, language text, theme text, verify text);
perms (id integer, admin integer, links integer, ban integer, upload integer);
flairs (id integer, name text, color text, creator integer, created integer);
'''

available_languages = ['en', 'de', 'jp']

class Void(): pass

db = 'db/accounts.db'

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

# User
def getNewUserID() -> int:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT MAX(id) FROM user')
    maxid = c.fetchone()
    conn.close()
    if maxid in [None, (None), (None,)]:
        return 1
    else:
        return maxid[0] + 1

def classfyUser(userObject: tuple, permsObject: tuple) -> Void():
    user = Void()
    user.id = userObject[0]
    user.mail = userObject[1]
    user.username = userObject[2]
    user.name = userObject[3]
    user.password = userObject[4]
    user.birthday = userObject[5]
    user.location = userObject[6]
    user.discord = userObject[7]
    user.description = userObject[8]
    user.website = userObject[9]
    user.image = userObject[10]
    user.banner = userObject[11]
    user.verification = userObject[12]
    user.fa = userObject[13]
    user.genres = userObject[14]
    flairs = userObject[15]
    flairlist = []
    for flair in flairs.split(","):
        if flair == '': continue
        flairlist.append(getFlair(int(flair)))
    user.flairs = flairlist
    user.favorites = userObject[16]
    user.language = userObject[17]
    user.theme = userObject[18]
    user.verify = userObject[19]
    user.perms = Void()
    user.perms.admin = bool(permsObject[1])
    user.perms.links = bool(permsObject[2])
    if user.perms.admin == True:
        user.perms.links = True
    if user.language == '': user.language = info['language']
    return user

def updateVerify(user: int, verify: str='True'):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('UPDATE user SET verify=? WHERE id=?', (verify, user))
    conn.commit()
    conn.close()

def getUser(id: int):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM user WHERE id=?', (id, ))
    user = c.fetchone()
    c.execute('SELECT * FROM perms WHERE id=?', (id, ))
    perms = c.fetchone()
    conn.close()
    if user == None: return None
    userinfo = user
    user = classfyUser(userinfo, perms)
    return user

def isUsernameTaken(username: str) -> bool:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM user WHERE username=?', (username,))
    e = c.fetchone()
    conn.close()
    if e in [None, (None,), (None), [None], []]:
        return False
    else:
        return True

def isMailTaken(mail: str) -> bool:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM user WHERE mail=?', (mail,))
    e = c.fetchone()
    conn.close()
    if e in [None, (None,), (None), [None], []]:
        return False
    else:
        return True

def createUser(username: str, mail: str, password: str, name: str='Display Name',
  birthday: int=0, location: str='', discord: str='', description: str='', website: str='',
  image: str='', banner: str='', verification: str='', twofa: str='', genres: str='',
  flairs: str='', favorites: str='', language: str='', verify: str='True'):
    '''The password should be clear text, that it can be hashed'''
    if getUserByMail(mail) != None or getUserByUsername(username) != None: return 'this mail/username is already taken'
    password = hashlib.sha512(bytes(password, 'utf-8')).hexdigest()
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT MAX(id) FROM user')
    maxid = c.fetchone()
    if maxid in [None, (None,), (None)]:
        id = 1
    else:
        id = maxid[0] + 1
    c.execute('INSERT INTO user VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (id, mail, username, name, password, birthday, location, discord, description, website, image, banner, verification, twofa, genres, flairs, favorites, language, 'default', verify))
    c.execute('INSERT INTO perms VALUES (?, ?, ?, ?, ?)', (id, False, False, False, False))
    conn.commit()
    conn.close()
    return id

def checkUserLogin(uauth: str, password: str) -> bool:
    """The password should be clear text, that it can be hashed"""
    password = hashlib.sha512(bytes(password, 'utf-8')).hexdigest()
    conn = sqlite3.connect(db)
    c = conn.cursor()
    if '@' in uauth:
        c.execute('SELECT * FROM user WHERE mail=? AND password=?', (uauth, password))
    else:
        c.execute('SELECT * FROM user WHERE username=? AND password=?', (uauth, password))
    user = c.fetchone()
    conn.close()
    if user == None:
        return False
    else:
        return True

def clearUserDB():
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('DELETE FROM user;')
    c.execute('DELETE from perms;')
    conn.commit()
    conn.close()

def getUserByMail(mail: str):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT id FROM user WHERE mail=?', (mail, ))
    id = c.fetchone()
    conn.close()
    if id in [None, (None, )]: return None
    user = getUser(id[0])
    return user

def getUserByUsername(username: str):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT id FROM user WHERE username=?', (username, ))
    id = c.fetchone()
    conn.close()
    if id in [None, (None, )]: return None
    user = getUser(id[0])
    return user

def deleteUser(id: int) -> None:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('DELETE FROM user WHERE id=?', (id, ))
    c.execute('DELETE FROM perms WHERE id=?', (id, ))
    conn.commit()
    conn.close()

def getAccountArea(min: int=1, max: int=10) -> list:
    """min=1 max=10 would return users with the id 1 to 10 (both inclusive)"""
    if min < 1: min = 1
    if max < min: max = min + 9
    users = []
    conn = sqlite3.connect(db)
    c = conn.cursor()
    for id in range(min, max + 1):
        c.execute('SELECT * FROM user WHERE id=?', (id, ))
        user = c.fetchone()
        c.execute('SELECT * FROM perms WHERE id=?', (id, ))
        perms = c.fetchone()
        if user == None: continue
        userinfo = user
        user = user = classfyUser(userinfo, perms)
        users.append(user)
    conn.close()
    return users


## Update
def updateLanguage(id: int, language: str):
    language = str(language).lower()
    if language not in available_languages:
        return 'language not available'
    else:
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute('UPDATE user SET language=? WHERE id=?', (language, id))
        conn.commit()
        conn.close()

def updateTheme(id: int, theme: str):
    theme = str(theme).lower()
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('UPDATE user SET theme=? WHERE id=?', (theme, id))
    conn.commit()
    conn.close()

def updateDescription(id: int, description: str):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('UPDATE user SET description=? WHERE id=?', (description, id))
    conn.commit()
    conn.close()

def updateName(id: int, name: str):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('UPDATE user SET name=? WHERE id=?', (name, id))
    conn.commit()
    conn.close()

def updateLocation(id: int, location: str):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('UPDATE user SET location=? WHERE id=?', (location, id))
    conn.commit()
    conn.close()

def updatePassword(id: int, password: str) -> None:
    password = hashlib.sha512(bytes(password, 'utf-8')).hexdigest()
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('UPDATE user SET password=? WHERE id=?', (password, id))
    conn.commit()
    conn.close()

def updateImage(id: int, image: str):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('UPDATE user SET image=? WHERE id=?', (image, id))
    conn.commit()
    conn.close()

def updateBanner(id: int, banner: str) -> None:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('UPDATE user SET banner=? WHERE id=?', (banner, id))
    conn.commit()
    conn.close()

def updateFaCode(id: int, code: str) -> None:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('UPDATE user SET twofa=? WHERE id=?', (code, id))
    conn.commit()
    conn.close()

# Flairs
"""color=#ffffff Werte"""
def getNewFlairID() -> int:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT MAX(id) FROM flairs')
    maxid = c.fetchone()
    conn.close()
    if maxid in [None, (None), (None,)]:
        return 1
    else:
        return maxid[0] + 1

def createFlair(name: str, color: str="#00007f", creator: int=0, created: int=time.time()) -> int:
    id = getNewFlairID()
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('INSERT INTO flairs VALUES (?, ?, ?, ?, ?)', (id, name, color, creator, created))
    conn.commit()
    conn.close()
    return id

def getFlair(id: int) -> dict:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM flairs WHERE id=?', (id, ))
    flair = c.fetchone()
    conn.close()
    f = {
        "id": flair[0],
        "name": flair[1],
        "color": flair[2],
        "creator": flair[3],
        "created": flair[4]
    }
    return f

def deleteFlair(id: int) -> None:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('DELETE FROM flairs WHERE id=?', (id,))
    conn.commit()
    conn.close()