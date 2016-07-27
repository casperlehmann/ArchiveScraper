"""Make sure that database fits files on disk.
"""
import sqlite3 as lite
import os
import re
from bs4 import BeautifulSoup as bs
import urllib.request

def page_contains_url(_url, _fname, path):
    "_"
    with open(os.path.join(path, _fname), 'rb') as _file:
        soup = bs(_file, 'html.parser', exclude_encodings=['windows-1252'])
    marker = r'/'.join(_url.split('/')[3:])
    res = re.search(marker, str(soup.contents))
    return bool(res), soup, res

def get_url(fname):
    "_"
    _id = int((fname+'|').strip('0')[:-1])
    with lite.connect('data/db') as con:
        cur = con.cursor()
        cur.execute('SELECT url FROM file_names WHERE id = ?', (_id,))
        url = cur.fetchall()[0][0]
        return url

def make_fname(num):
    "_"
    if not isinstance(num, int):
        raise ValueError('num must be an integer.')
    if num < 1:
        raise ValueError('num must be a positive integer.')
    return str(num).zfill(6)

def make_id(string):
    "_"
    if not isinstance(string, str):
        raise ValueError('string must be a str.')
    return int((string+'|').strip('0')[:-1])

def get_online_page(url):
    "_"
    try:
        with urllib.request.urlopen(url) as url_obj:
            return url_obj.read()
    except:
        return ''

def clean_print(string):
    print (re.sub('\s+', ' ', string))

def compare(num):
    "_"
    with lite.connect('data/db') as con:
        cur = con.cursor()
        cur.execute('SELECT * FROM file_names WHERE id = ?', (num,))
        try:
            url, _id, scanned, four_o_four = cur.fetchone()
        except TypeError:
            return 'no_file'
    fname = make_fname(num)
    contains, soup, res = page_contains_url(url, fname, path = 'data/archives')
    contents = str(soup.contents)
    start, end = res.start(), res.end()
    start_plus, end_plus = max(0, start-140), min(res.endpos, end+80)
    epilogue = contents[end:end_plus]
    prologue = contents[start_plus:start]
    if 'var title' in epilogue:
        #print (contents[start:end])
        return 'title'
    if 'news_title' in prologue:
        return 'news'
    if 'http-equiv="mobile-agent"' in epilogue:
        return 'agent'
    if 'to_friend' in prologue:
        return 'to_friend'
    if 'abl2' in epilogue:
        return 'abl2'
    if epilogue.startswith('">【1'):
        return 'first_page'
    print ()
    print (fname, ':', start)
    clean_print (contents[start:end])
    clean_print (contents[start_plus:end_plus])
    print ()
    return False

# 1 - 1517 archive
# 1518 works
# START, END = 1519, 5640 does not exist.
# START, END = 5641, 5910 #works
#START, END = 5910, 6000 # partly works
START, END = 6000, 7000
START, END = 1517, 10000
START, END = 10000, 20000
START, END = 20000, 80000
#START, END = 48974, 48975
START, END = 1519, 5641

non_match = [5928, 5929] + [47694, 48458, 49257, 49263, 49416, 49422, 49650, 49912, 50165, 50266, 50447, 50668, 51047, 51411, 51583, 52105, 52111, 52125, 52448, 52469, 52557, 53147, 53206, 53295, 53366, 53500, 53761, 53842, 53858, 54294, 54296, 54399, 54477, 55240, 55688, 55919, 55926, 56071, 57104, 57318, 57563, 57576, 58297, 58351, 58404, 58418, 58738, 58829, 58943, 59044, 59172, 59271, 59678, 60039, 60332, 60553, 60805, 61262, 61356, 61516, 61518, 61531, 61535, 61537, 61567, 61649, 62219, 62442, 62555, 62631, 62641, 62737, 62816, 63466, 63895, 63929, 64000, 64923, 65010, 65036, 65470]

no_file = [1685, 5915, 6062] + [14393]
# [62442] is a forum discussion. Everchanging.
ALL = non_match + no_file

ALL = list(range(START, END))

from time import time
import socket
begyndelse = time()
#START, END = 5793, 5800
match_online = []
non_match_online = []
no_file = []
timed_out = []
d = {}
for i in ALL:#list(range(START, END)):#range(1000, 50000, 493):
    try:
        res = compare(i)
        if res == 'no_file':
            no_file.append(i)
        else:
            d[i] = res
    except FileNotFoundError:
        print (i, 'not found.')
    except socket.timeout:
        print (i, 'timed out')
        timed_out.append(i)
    except AttributeError:
        name = make_fname(i)
        url = get_url(name)
        print (i, 'does not contain url:', url)
        try:
            fetched = get_online_page(url)
            with open(os.path.join('data/archives', name), 'rb') as _file:
                that = bs(fetched, 'html.parser')
                this = bs(_file, 'html.parser')
                # 48974 causes a problem, if we don't use text.
                matches = that.text == this.text
                #print (re.sub('\s+', ' ', that.text))
                #print (re.sub('\s+', ' ', this.text))
                print ('It is OK:', matches)
                if matches:
                    match_online.append(i)
                    d[i] = 'match_online'
                else:
                    non_match_online.append(i)
        except:
            non_match_online.append(i)


title = 0
agent = 0
news = 0
to_friend = 0
abl2 = 0
first_page = 0
true = 0
false = 0
for k, v in d.items():
    #print ('{:>6} {}'.format(k, v))
    #print (get_url(make_fname(k)))
    if not v:
        false += 1
    else:
        true += 1
        if v == 'title': title += 1
        elif v == 'agent': agent += 1
        elif v == 'news': news += 1
        elif v == 'to_friend': to_friend += 1
        elif v == 'abl2': abl2 += 1
        elif v == 'first_page': first_page += 1
        #elif v == 'no_file': no_file += 1
        else: print (v)
print (80*'=')
print ('in all:', true)
print ('false:', false)
print ('title:', title)
print ('agent:', agent)
print ('news:', news)
print ('to_friend', to_friend)
print ('abl2', abl2)
print ('first_page', first_page)
print ()


print ('Start: {}, End: {}'.format(START, END))
_all = sum([title, agent, news, to_friend, abl2, first_page, len(match_online)
           ])
print ('{} / {}: {}'.format(_all, true, _all == true))
print ()

print ('match_online', len(match_online))
print (match_online)
print ()
print ('non_match_online', len(non_match_online))
print (non_match_online)
print ()
print ('no_file', len(no_file))
print (no_file)
print ('timed_out', len(timed_out))
print (timed_out)

slutning = time()

print ()
print ('tid:', begyndelse, slutning, slutning-begyndelse)
