import sqlite3 as lite

with lite.connect('data/db') as con:
    cur = con.cursor()
    cur.execute('SELECT url FROM file_names')
    _ = cur.fetchall()
    __ = set(_)
    print (len(_) == len(__))
    print (sorted(_) == sorted(__))
    print (_[-10:])
