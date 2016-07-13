"""Functions to match urls with regular expressions.
"""
import re

# pylint: disable=unused-variable

def match_Y_MD_cCATALOGUE_CONTENT(url, data):
    """# matches of n:
    # http://politics.people.com.cn/n/2013/0122/c70731-20290308.html
    # http://politics.people.com.cn/n1/2016/0111/c70731-28039057.html
    """
    exp = (r'(?<=.people.com.cn/)'
           r'(?:n|n1|GB)/'
           r'([0-6]*)/'
           r'([0-1][0-9])'
           r'([0-3][0-9])/'
           r'c([0-9]*)'
           r'-([0-9]*)'
           r'(?=.html)')
    findall = re.findall(exp, url)
    #print()
    #print ('|', 'match_Y_MD_cCATALOGUE_CONTENT')
    #print ('|', findall)
    if len(findall) > 0:
        findall = findall[0]
    if len(findall) == 5:
        year, month, day, _catalogs, _content_id = findall
        #print (_content_id)
        id_match = match_content_id(_content_id, url, data)
        #print ('match', match)
        #for fname, content_id, catalogs, date_string in data:
        #    print (_content_id, content_id)
        #    input()
        #print ('rematch', _content_id in ids)
        #ids = [content_id for fname, content_id, catalogs, date_string in data]
        #print ('rematch', _content_id in ids)
        return id_match
    return False

def match_num_num(url, data):
    """ matches of GB/num/num:
    # http://politics.people.com.cn/GB/70731/17086009.html
    # http://society.people.com.cn/GB/41260/18092656.html
    """
    exp = (r'(?<=.people.com.cn/)'
           r'(?:n|n1|GB)/'
           r'([0-9]*)/'
           r'([0-9]*)'
           r'(?=.html)')
    findall = re.findall(exp, url)
    if len(findall) > 0:
        findall = findall[0]
    if len(findall) == 2:
        _catalogs, _content_id = findall
        #print ('match_num_num')
        return match_content_id(_content_id, url, data)
    return False

def match_GB_4_num(url, data):
    """ matches of GB/num/num/num/num
    # http://politics.people.com.cn/GB/8198/243877/243886/18105453.html
    """
    exp = (r'(?<=.people.com.cn/GB/)'
           r'([0-9]*)/'
           r'([0-9]*)/'
           r'([0-9]*)/'
           r'([0-9]*)'
           r'(?=.html)')
    findall = re.findall(exp, url)
    if len(findall) > 0:
        findall = findall[0]
    if len(findall) == 4:
        _, _, _, _content_id = findall
        #print ('match_GB_4_num')
        return match_content_id(_content_id, url, data)
    return False

def match_GB_shizheng(url, data):
    """
    http://politics.people.com.cn/GB/shizheng/252/10043/10044/17360292.html
    """
    exp = (r'(?<=.people.com.cn/GB/)'
           r'(shizheng)/'
           r'([0-9]*)/'
           r'([0-9]*)/'
           r'([0-9]*)/'
           r'([0-9]*)'
           r'(?=.html)')
    findall = re.findall(exp, url)
    if len(findall) > 0:
        findall = findall[0]
    if len(findall) == 5:
        _, _, _, _, _content_id = findall
        #print ('match_GB_shizheng')
        return match_content_id(_content_id, url, data)
    return False

def match_GB_num_review_num(url, data):
    """ Not in use.
    matches of GB/num/review/num:
    # http://politics.people.com.cn/GB/70731/review/20151102.html"""
    exp = (r'(?<=.people.com.cn/GB/)'
           r'([0-9]*)/'
           r'(review)/'
           r'([0-9]*)'
           r'(?=.html)')
    findall = re.findall(exp, url)
    if len(findall) > 0:
        findall = findall[0]
    if len(findall) == 3:
        _, _, _content_id = findall
        #print ('match_GB_num_review_num')
        data = data
        return
        # return match_content_id(_content_id, url, data)
    return False

def match_GB_num(url, data):
    """ matches of GB/num:
    # http://politics.people.com.cn/GB/17996105.html
    # http://society.people.com.cn/GB/17110600.html
    """
    exp = (r'(?<=.people.com.cn/GB/)'
           r'([0-9]*)'
           r'(?=.html)')
    findall = re.findall(exp, url)
    # Only one match, so no need to unpack.
    #if len(findall) > 0:
    #    findall = findall[0]
    if len(findall) == 1:
        _content_id = findall[0]
        #print ('match_GB_num')
        return match_content_id(_content_id, url, data)
    return False

def match_Ycppccnpc_GB_num(url, data):
    """
    # http://lianghui.people.com.cn/2012npc/GB/17321914.html
    """
    exp = (r'(?<=.people.com.cn/)'
           r'[0-6]*(?:cppcc|npc)/'
           r'(?:n|n1|GB)/'
           r'([0-9]*)'
           r'(?=.html)')
    findall = re.findall(exp, url)
    # Only one match, so no need to unpack.
    #if len(findall) > 0:
    #    findall = findall[0]
    if len(findall) == 1:
        _content_id = findall[0]
        #print ('match_Ycppccnpc_GB_num')
        return match_content_id(_content_id, url, data)
    return False

def match_blog_article_num(url, data):
    """ matches of blog.../article/num
    # http://blog.people.com.cn/article/1/1348212580745.html"""
    exp = (r'(?<=http://blog.people.com.cn/article/)'
           r'([0-9]+)/'
           r'([0-9]+)'
           r'(?=.html)')
    findall = re.findall(exp, url)
    if len(findall) > 0:
        findall = findall[0]
    if len(findall) == 2:
        _, _content_id = findall
        #print ('match_blog_article_num')
        return match_content_id(_content_id, url, data)
    return False

def match_Ycppcnpc_MD_cCATALOGUE_CONTENT(url, data):
    """
    # http://lianghui.people.com.cn/2016cppcc/n1/2016/0304/c402626-28172916.html
    """
    exp = (r'(?<=.people.com.cn/)'
           r'[0-6]*(?:cppcc|npc)/'
           r'(?:n|n1|GB)/'
           r'([0-6]*)/'
           r'([0-1][0-9])'
           r'([0-3][0-9])/'
           r'c([0-9]*)'
           r'-([0-9]*)'
           r'(?=.html)')
    findall = re.findall(exp, url)
    if len(findall) > 0:
        #print(findall)
        #input()
        findall = findall[0]
    if len(findall) == 5:
        year, month, day, _catalogs, _content_id = findall
        #print ('match_Ycppcnpc_MD_cCATALOGUE_CONTENT')
        return match_content_id(_content_id, url, data)
    return False

def match(year, month, day, _catalogs, _content_id, url, data):
    """Match on multiple parameters.
    """
    _date_string = '{}-{}-{}'.format(year, month, day)
    for fname, content_id, catalogs, date_string in data:
        #70731 23519224 2013-11-12 70731 23093028 2013-10-01
        #if [catalogs, content_id, date_string] == [_catalogs, _content_id, _date_string]:
        if [catalogs, content_id] == [_catalogs, _content_id]:
            return {
                'fname': fname,
                'url': url,
                'catalogs': catalogs,
                'content_id': content_id,
                'date_string': date_string}

def match_content_id(_content_id, url, data):
    """Match url to data on content_id
    """
    for fname, content_id, catalogs, date_string in data:
        #if not isinstance(_content_id, str):
        #    print (_content_id, content_id)
        #    input()
        if content_id == _content_id:
            return {
                'fname': fname,
                'url': url,
                'catalogs': catalogs,
                'content_id': content_id,
                'date_string': date_string}
