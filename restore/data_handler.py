"_"
import sqlite3 as lite
import json
import os

from restore import page_identifier, page_mapper, page_contains_url

def get_all_links(restore_path):
    "_"
    try:
        all_links = json.load(
            open(os.path.join(restore_path, 'all_links.json'), 'r'))
    except FileNotFoundError:
        with lite.connect(os.path.join(restore_path, 'db')) as con:
            cur = con.cursor()
            all_links = list(set(
                _[0] for _ in cur.execute(
                    'SELECT link FROM links WHERE url != "seed"').fetchall()))
        json.dump(
            list(all_links),
            open(os.path.join(restore_path, 'all_links.json'), 'w'))
        #exit()
    return all_links

def get_page_data(path, restore_path):
    "_"
    try:
        #open('q', 'r')
        missing_data = json.load(
            open(os.path.join(restore_path, 'missing_data.json'), 'r'))
        page_data = json.load(
            open(os.path.join(restore_path, 'page_data.json'), 'r'))
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
        json.dump(
            missing_data,
            open(os.path.join(restore_path, 'missing_data.json'), 'w'))
        json.dump(
            page_data,
            open(os.path.join(restore_path, 'page_data.json'), 'w'))
        #exit()
    return page_data, missing_data

def get_mapping(all_links, page_data, names_and_funcs, restore_path, path):
    "_"
    try:
        mapping = json.load(
            open(os.path.join(restore_path, 'mapping.json'), 'r'))
    except FileNotFoundError:
        sad = 0
        happy = 0
        results = []
        mapping = {}
        for i, link in enumerate(all_links):
            for result in page_mapper(link, page_data, names_and_funcs):
                url = result['url']
                fname = result['fname']
                if page_contains_url(url, fname, path):
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
        json.dump(
            mapping, open(os.path.join(restore_path, 'mapping.json'), 'w'))
        #exit()
    return mapping
