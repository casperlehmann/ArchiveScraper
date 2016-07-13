"""_
"""
import re

from bs4 import BeautifulSoup as bs

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
    Y_MD_cCATALOGUE_CONTENT = _names_and_funcs['Y_MD_cCATALOGUE_CONTENT'](_url, _data)
    if Y_MD_cCATALOGUE_CONTENT is not None:
        yield Y_MD_cCATALOGUE_CONTENT

    Ycppcnpc_MD_cCATALOGUE_CONTENT = _names_and_funcs['Ycppcnpc_MD_cCATALOGUE_CONTENT'](_url, _data)
    if Ycppcnpc_MD_cCATALOGUE_CONTENT is not None:
        yield Ycppcnpc_MD_cCATALOGUE_CONTENT

    num_num = _names_and_funcs['num_num'](_url, _data)
    if num_num is not None:
        yield num_num

    GB_4_num = _names_and_funcs['GB_4_num'](_url, _data)
    if GB_4_num is not None:
        yield GB_4_num

    GB_num = _names_and_funcs['GB_num'](_url, _data)
    if GB_num is not None:
        yield GB_num

    Ycppccnpc_GB_num = _names_and_funcs['Ycppccnpc_GB_num'](_url, _data)
    if Ycppccnpc_GB_num is not None:
        yield Ycppccnpc_GB_num

    blog_article_num = _names_and_funcs['blog_article_num'](_url, _data)
    if blog_article_num is not None:
        yield blog_article_num

    # Archive pages. Can match on 'catalogs', but would be time consuming.
    #GB_num_review_num = _names_and_funcs['GB_num_review_num'](_url, _data)
    #if GB_num_review_num is not None:
    #    yield GB_num_review_num

def page_contains_url(_url, _fname):
    "_"
    with open(
        '/Users/Lasper/safe data/_data_dearchiver/2_articles/{}'.format(_fname),
        'rb') as _file:
        soup = bs(_file, 'html.parser', exclude_encodings=['windows-1252'])
    marker = r'/'.join(_url.split('/')[3:])
    res = re.search(marker, str(soup.contents))
    return bool(res)
