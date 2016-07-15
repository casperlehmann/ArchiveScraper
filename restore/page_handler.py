"""_
"""
import re
import os

from bs4 import BeautifulSoup as bs

# pylint: disable=unused-variable

def page_identifier(_path, num):
    "_"
    str_num = str(num).zfill(6)
    with open(_path + str_num, 'rb') as _file:
        soup = bs(_file, 'html.parser', exclude_encodings=['windows-1252'])
        #soup = bs(_file, 'html.parser', exclude_encodings=['gb2312'])
        #soup = bs(_file, 'html.parser', exclude_encodings=['utf-8'])
        #print (soup.original_encoding)
        #try: soup.encode('utf')
        #except: soup = soup.decode('utf')

    for script in soup(["script", "style"]):
        script.extract()
    #_text = soup.text
    #_text = re.sub(r'\n+', r'\n', _text)
    #_text = re.sub(r'\t+', r'', _text)
    #_text = re.sub(r'( )+', r' ', _text)
    #print (_text)

    (_content_id, _catalogs, _publish_date) = (None, None, None)
    for meta in soup.find_all('meta'):
        if meta.has_attr('name'):
            if meta['name'] == 'catalogs':
                _catalogs = meta['content']
                #print ('_catalogs:', _catalogs)
            if meta['name'] == 'contentid':
                _content_id = meta['content']
                #print ('_content_id:', _content_id)
            if meta['name'] == 'publishdate':
                _publish_date = meta['content']
                #print ('publishdate:', _publish_date)
            if not None in (_content_id, _catalogs, _publish_date):
                break
    return _catalogs, _content_id, _publish_date

def page_mapper(_url, _data, _names_and_funcs):
    "_"
    for name, func in _names_and_funcs:
        result = func(_url, _data)
        if not result in (None, False):
            yield result
    # Archive pages. Can match on 'catalogs', but would be time consuming.
    #GB_num_review_num = _names_and_funcs['GB_num_review_num'](_url, _data)
    #if GB_num_review_num is not None:
    #    yield GB_num_review_num

def page_contains_url(_url, _fname, path):
    "_"
    with open(os.path.join(path, _fname), 'rb') as _file:
        soup = bs(_file, 'html.parser', exclude_encodings=['windows-1252'])
    marker = r'/'.join(_url.split('/')[3:])
    res = re.search(marker, str(soup.contents))
    return bool(res)
