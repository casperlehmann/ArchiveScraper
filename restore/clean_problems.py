import os
import socket
import urllib.request
import sqlite3 as lite

non_match = [5928, 5929] + [47694, 48458, 49257, 49263, 49416, 49422, 49650, 49912, 50165, 50266, 50447, 50668, 51047, 51411, 51583, 52105, 52111, 52125, 52448, 52469, 52557, 53147, 53206, 53295, 53366, 53500, 53761, 53842, 53858, 54294, 54296, 54399, 54477, 55240, 55688, 55919, 55926, 56071, 57104, 57318, 57563, 57576, 58297, 58351, 58404, 58418, 58738, 58829, 58943, 59044, 59172, 59271, 59678, 60039, 60332, 60553, 60805, 61262, 61356, 61516, 61518, 61531, 61535, 61537, 61567, 61649, 62219, 62442, 62555, 62631, 62641, 62737, 62816, 63466, 63895, 63929, 64000, 64923, 65010, 65036, 65470]

no_file = [1685, 5915, 6062] + [14393]

ALL = non_match + no_file

ALL = [1685, 5915, 6062]

### NEW = list(range(1519, 5641))
NEW = list(range(1519, 1732))
#broken 404: NEW = [1732] http://blog.people.com.cn/open/articleFine.do?articleId=1344993673714&sT=1
NEW = list(range(1733, 1820))
#Forbidden: NEW = [1820]
NEW = list(range(1821, 1834))
#broken 404: NEW = [1834] http://politics.people.com.cn/GB/1024/17475413.html
NEW = list(range(1835, 1909))
#broken 404: NEW = [1909] http://politics.people.com.cn/n/2012/0707/c1024-18466493.html
NEW = list(range(1910, 2279))
#Forbidden 404: NEW = [2279] http://politics.people.com.cn/n/2013/0125/c70731-20327938.html
NEW = list(range(2280, 4284)) # OK
NEW = list(range(4284, 5641))
NEW = []

four_o_four = [1732, 1820, 1834, 1909, 2279]

not_four_o_four = [1661, 1766, 1768, 1770, 1771, 1772, 1851, 1852, 1946, 1949, 1951, 1953, 2159, 2166, 2279, 2293, 2296]

def set_404(nums):
    with lite.connect('data/db') as con:
        cur = con.cursor()
        cur.execute(
            'UPDATE file_names SET four_o_four = 1 WHERE id IN ({})'.format(
                ', '.join(len(nums)*['?'])), nums)
        cur.execute(
            'SELECT id, url, scanned, four_o_four FROM file_names WHERE id IN ({})'.format(
                ', '.join(len(nums)*['?'])), nums)
        urls = [_[0] for _ in cur.fetchall()]
        urls = cur.fetchall()
        for _ in urls: print (_)
        return urls

#set_404(four_o_four)

def check_files_exist():
    with lite.connect('data/db') as con:
        cur = con.cursor()
        cur.execute('SELECT id, url, scanned, four_o_four FROM file_names WHERE four_o_four = 0')
        rows = cur.fetchall()
        for _ in rows:
            if not os.path.isfile(get_filepath(_[0])):
                print (_)
        else:
            print ('all good')
        cur.execute('SELECT id, url, scanned, four_o_four FROM file_names WHERE four_o_four = 1')
        rows = cur.fetchall()
        for _ in rows:
            if os.path.isfile(get_filepath(_[0])):
                print (_)
        else:
            print ('all good')

#ALL = [_ for _ in ALL if not _ in [5928, 5929, 14393, 47694, 48458, 49257, 49263, 49416, 49422, 49650]]

#print (len(ALL))
#print ('*')
#print (ALL)

def get_urls(nums):
    with lite.connect('data/db') as con:
        cur = con.cursor()
        cur.execute(
            'SELECT id, url FROM file_names WHERE id IN ({})'.format(
                ', '.join(len(nums)*['?'])), nums)
        #urls = [_[0] for _ in cur.fetchall()]
        urls = cur.fetchall()
        return urls

def get_online_page(url, n = 0, num = 0):
    "_"
    try:
        with urllib.request.urlopen(url, None, 5) as url_obj:
            return url_obj.read()
    except urllib.error.HTTPError:
        print('\t\t\t\t#Forbidden 404: NEW = [{}] {}'.format(num, url))
    except:#socket.timeout urllib.error.URLError:
        n += 1
        if n > 5:
            print (url, 'cannot be reached. Exiting.')
            exit()
        return get_online_page(url, n = n, num = num)

def get_temppath(num):
    return 'data/temp/'+str(num).zfill(6)

def get_filepath(num):
    return 'data/archives/'+str(num).zfill(6)

def new_filepath(num):
    return 'data/unverifiable/'+str(num).zfill(6)

check_files_exist()
exit()


#for num, url in get_urls(ALL):
#    print (num, url)
#    old_path = get_filepath(num)
#    new_path = new_filepath(num)
#    page = get_online_page(url)
#    os.rename(old_path, new_path)
#    with open(old_path, 'wb') as f:
#        f.write(page)

def get_final(urls):
    for num, url in get_urls(urls):
        print (num, url)
        temp_path = get_temppath(num)
        page = get_online_page(url, num = num)
        if not page is None:
            with open(temp_path, 'wb') as f:
                f.write(page)

while True:
    get_final(NEW[:100])
    if len(NEW) > 100:
        NEW = NEW[100:]
    else:
        break




