"""See if file matches online version.
"""
import sqlite3 as lite
import urllib.request
import os
from bs4 import BeautifulSoup as bs

def get_url(fname):
    "_"
    _id = int((fname+'|').strip('0')[:-1])
    with lite.connect('data/db') as con:
        cur = con.cursor()
        cur.execute('SELECT url FROM file_names WHERE id = ?', (_id,))
        url = cur.fetchall()[0][0]
        return url

def get_filename(url):
    "_"
    with lite.connect('data/db') as con:
        cur = con.cursor()
        cur.execute('SELECT id FROM file_names WHERE url = ?', (url,))
        row = cur.fetchall()
        if len(row) == 0:
            print ('No record of url', url)
            print()
            return
        fname = str(row[0][0]).zfill(6)
        return fname

def get_online_page(url):
    "_"
    with urllib.request.urlopen(url) as url_obj:
        return url_obj.read()

def get_local_page(fname):
    "_"
    path = 'data/archives'
    fpath = os.path.join(path, fname)
    with open(fpath, 'rb') as f:
        return f.read()

def compare(url = None, fname = None):
    "_"
    if url is None and fname is None:
        return
    if fname is None:
        fname = get_filename(url)
    if url is None:
        url = get_url(fname)
    online = get_online_page(url)
    try:
        offline = get_local_page(fname)
    except FileNotFoundError:
        offline = 'Offline: Nada.'
    if online != offline:
        #for i in range(int(len(online)/80)):
        #    print (online[i:i+80])
        #    print (offline[i:i+80])
        print ('>', fname, url)
        print ('>	', online[:100])
        print(80*'=')
        print ('>	', offline[:100])
        #print ('>	', bs(online, 'html.parser').text[:1000])
        #print(80*'=')
        #print ('>	', bs(offline, 'html.parser').text[:1000])
        #print (fname, url)
        print ()
    else:
        print ('OK:', fname, url)


URL = 'http://politics.people.com.cn/n/2014/0909/c1024-25628501.html'
#URL = 'http://politics.people.com.cn/GB/1026/14942055.html'
#compare(URL)

with lite.connect('data/db') as con:
    cur = con.cursor()
    cur.execute('SELECT * from file_names')
    for row in cur.fetchall():
        print (row)

#num = 1100
#string = str(num).zfill(6)
#print(get_url(string))
#compare(fname = string)

#[1592,1628,1520, 1679]
#for num in range(29, 50):#range(1100,112000,320):
for num in [16, 190, 1001, 2300, 5000, 13054, 15902, 24039, 40195, 55632, 60000]:
    #range(1519, 1530):
    string = str(num).zfill(6)
    compare(fname = string)

#print ()
#url = 'http://politics.people.com.cn/GB/70731/review/20151003.html'
#with lite.connect('data/db') as con:
#    cur = con.cursor()
#    cur.execute('SELECT * FROM file_names WHERE url = ?', (url,))
#    cur.execute('SELECT * FROM file_names')
#    cur.execute('SELECT * FROM links WHERE fetched = 1')
#    for _ in cur.fetchall():
#        print (_)
#    print()
#    #cur.execute('SELECT * FROM links')
#    #for _ in cur.fetchall():
#    #    print (_)
