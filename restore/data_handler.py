"_"
import sqlite3 as lite
import json

from restore import page_identifier, page_mapper, page_contains_url

def get_all_links():
    "_"
    try:
        all_links = json.load(open('all_links', 'r'))
    except FileNotFoundError:
        with lite.connect('data/db') as con:
            cur = con.cursor()
            all_links = list(set(
                _[0] for _ in cur.execute('SELECT link FROM links').fetchall()))
        json.dump(list(all_links), open('all_links', 'w'))
        exit()
    return all_links

def get_page_data(path):
    "_"
    try:
        #open('q', 'r')
        missing_data = json.load(open('missing_data', 'r'))
        page_data = json.load(open('page_data', 'r'))
    except FileNotFoundError:
        missing_data = []
        page_data = []
        for x in range(15478):#1600, 11600):
            catalogs, content_id, publish_date = page_identifier(path, x)
            fname = str(x).zfill(6)
            if None in (content_id, catalogs, publish_date):
                print ('file name:', fname,
                       'catalogs:', catalogs,
                       'content_id:', content_id,
                       'publishdate:', publish_date)
                missing_data.append((fname, content_id, catalogs, publish_date))
            else:
                page_data.append((fname, content_id, catalogs, publish_date))
        json.dump(missing_data, open('missing_data', 'w'))
        json.dump(page_data, open('page_data', 'w'))
        exit()
    return page_data, missing_data

def get_mapping(all_links, page_data, names_and_funcs):
    "_"
    try:
        mapping = json.load(open('mapping.json', 'r'))
    except FileNotFoundError:
        sad = 0
        happy = 0
        results = []
        mapping = {}
        for i, link in enumerate(all_links[:10000]):
            for result in page_mapper(link, page_data, names_and_funcs):
                url = result['url']
                fname = result['fname']
                if page_contains_url(url, fname):
                    mapping[url] = fname
                    happy += 1
                    break
                else:
                    continue
                results.append(result)
                if i % 100 == 0:
                    print (i, '/', len(all_links))
            else:
                sad += 1
        print ('happy:', happy)
        print ('sad:', sad)
        json.dump(mapping, open('mapping.json', 'w'))
        exit()
    return mapping
