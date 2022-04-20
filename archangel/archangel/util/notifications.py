import sqlite3
import time
import json

db = 'db/notifications.db'

"""
notifications (id integer, user integer, read integer, date integer, sender integer, reason text, title text, text text, type text, footer text, buttons text, duration integer, inbox integer)
"""

class Notification():
    def __init__(self, id: int, user: int, read: bool, date: int, sender: int, reason: str, title: str, text: str, type: str, footer: str, buttons: list, duration: int):
        self.id = id
        self.user = user
        self.read = bool(read)
        self.date = date
        self.sender = sender
        self.reason = reason
        self.title = title
        self.text = text
        self.type = type
        self.footer = footer
        self.buttons = buttons
        self.duration = duration
 

def newNotificationID() -> int:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT MAX(id) FROM notifications')
    maxid = c.fetchone()
    conn.close()
    if maxid in [None, (None), (None,)]:
        return 1
    else:
        return maxid[0] + 1

def newNotification(user: int, duration: int=0, sender: int=0, reason: str='', title: str='', text: str='', type: str='info', footer: str='', buttons: list=[], inbox: bool=True, date: int=time.time()) -> int:
    """buttons example=[{'text': 'text', 'onclick': 'alert(\'clicked!\');'}]"""
    buttonstring = json.dumps(buttons)
    id = newNotificationID()
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('INSERT INTO notifications VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (id, user, 0, date, sender, reason, title, text, type, footer, buttonstring, duration, inbox))
    conn.commit()
    conn.close()
    return id

def getNotification(id: int) -> Notification:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM notifications WHERE id=?', (id,))
    notification = c.fetchone()
    conn.close()
    if notification in [None, (None, ), (None)]:
        return None
    buttons = buttonStringToButtons(notification[10])
    notification_type = Notification(id, notification[1], notification[2], notification[3], notification[4], notification[5], notification[6], notification[7], notification[8], notification[9], buttons, notification[11])
    return notification_type

def getNewestNotifications(user: int, count: int=15) -> list:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM notifications WHERE user=? AND inbox=1 ORDER BY date DESC', (user, ))
    nots = c.fetchmany(size=count)
    conn.close()
    notifications = []
    for notification in nots:
        buttons = buttonStringToButtons(notification[10])
        
        notification_type = Notification(notification[0], notification[1], notification[2], notification[3], notification[4], notification[5], notification[6], notification[7], notification[8], notification[9], buttons, notification[11])
        notifications.append(notification_type)
    return notifications 

def getUnreadUserNotifications(user: int, setRead: bool=True) -> list:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM notifications WHERE user=? AND read=0', (user, ))
    nots = c.fetchall()
    
    notifications = []
    for notification in nots:
        if notification in [None, (None, ), (None)]:
            continue
        buttons = buttonStringToButtons(notification[10])
        
        notification_type = Notification(notification[0], notification[1], notification[2], notification[3], notification[4], notification[5], notification[6], notification[7], notification[8], notification[9], buttons, notification[11])
        notifications.append(notification_type)
    c.execute('UPDATE notifications SET read=1 WHERE user=?', (user, ))
    conn.commit()
    conn.close()
    return notifications


def buttonStringToButtons(buttonString) -> list:
    buttons = json.loads(buttonString)
    return buttons