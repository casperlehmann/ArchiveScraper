"_"
import re

def analyze_coverage(_data, names_and_funcs, all_links):
    "_"
    fit_sum = 0
    count_sum = 0
    count_filtered = 0

    fit_Y_MD_cCATALOGUE_CONTENT = 0
    fit_Ycppcnpc_MD_cCATALOGUE_CONTENT = 0
    fit_num_num = 0
    fit_GB_4_num = 0
    fit_GB_num = 0
    fit_Ycppccnpc_GB_num = 0
    fit_blog_article_num = 0

    count_Y_MD_cCATALOGUE_CONTENT = 0
    count_Ycppcnpc_MD_cCATALOGUE_CONTENT = 0
    count_num_num = 0
    count_GB_4_num = 0
    count_GB_num = 0
    count_Ycppccnpc_GB_num = 0
    count_blog_article_num = 0

    names_and_funcs = {k: v for (k,v) in names_and_funcs}

    for _i, link in enumerate(all_links):#[:3]:
        i = _i + 1
        #print (i)
        if (filter_pages(link)) is True:
            count_filtered += 1
        Y_MD_cCATALOGUE_CONTENT = names_and_funcs['Y_MD_cCATALOGUE_CONTENT'](link, _data)
        if not Y_MD_cCATALOGUE_CONTENT is False:
            fit_Y_MD_cCATALOGUE_CONTENT += 1
            if Y_MD_cCATALOGUE_CONTENT is not None:
                count_Y_MD_cCATALOGUE_CONTENT += 1
        Ycppcnpc_MD_cCATALOGUE_CONTENT = names_and_funcs['Ycppcnpc_MD_cCATALOGUE_CONTENT'](link, _data)
        if not Ycppcnpc_MD_cCATALOGUE_CONTENT is False:
            fit_Ycppcnpc_MD_cCATALOGUE_CONTENT += 1
            if Ycppcnpc_MD_cCATALOGUE_CONTENT is not None:
                count_Ycppcnpc_MD_cCATALOGUE_CONTENT += 1
        num_num = names_and_funcs['num_num'](link, _data)
        if not num_num is False:
            fit_num_num += 1
            if num_num is not None:
                count_num_num += 1
        GB_4_num = names_and_funcs['GB_4_num'](link, _data)
        if not GB_4_num is False:
            fit_GB_4_num += 1
            if GB_4_num is not None:
                count_GB_4_num += 1
        GB_num = names_and_funcs['GB_num'](link, _data)
        if not GB_num is False:
            fit_GB_num += 1
            if GB_num is not None:
                count_GB_num += 1
        Ycppccnpc_GB_num = names_and_funcs['Ycppccnpc_GB_num'](link, _data)
        if not Ycppccnpc_GB_num is False:
            fit_Ycppccnpc_GB_num += 1
            if Ycppccnpc_GB_num is not None:
                count_Ycppccnpc_GB_num += 1
        blog_article_num = names_and_funcs['blog_article_num'](link, _data)
        if not blog_article_num is False:
            fit_blog_article_num += 1
            if blog_article_num is not None:
                count_blog_article_num += 1

        if sum([
                int(Y_MD_cCATALOGUE_CONTENT is not False),
                int(Ycppcnpc_MD_cCATALOGUE_CONTENT is not False),
                int(num_num is not False),
                int(GB_4_num is not False),
                int(GB_num is not False),
                int(Ycppccnpc_GB_num is not False),
                int(blog_article_num is not False)]) > 0:
            fit_sum += 1

        if sum([
                int(Y_MD_cCATALOGUE_CONTENT not in [None, False]),
                int(Ycppcnpc_MD_cCATALOGUE_CONTENT not in [None, False]),
                int(num_num not in [None, False]),
                int(GB_4_num not in [None, False]),
                int(GB_num not in [None, False]),
                int(Ycppccnpc_GB_num not in [None, False]),
                int(blog_article_num not in [None, False])]) > 0:
            count_sum += 1

        if i % 100 == 0:
            print ('Fit: {} / {} = {}%'.format(
                fit_sum, i, round(fit_sum/i*100, 2)))
            print ('Count: {} / {} = {}%'.format(
                count_sum, i, round(count_sum/i*100, 2)))
            print ('Filtered: {} / {} = {}%'.format(
                count_filtered, i, round(count_filtered/i*100, 2)))
            print ('{:<30} - fit: {:>10} count: {:10}'.format(
                'Y_MD_cCATALOGUE_CONTENT',
                fit_Y_MD_cCATALOGUE_CONTENT,
                count_Y_MD_cCATALOGUE_CONTENT))
            print ('{:<30} - fit: {:>10} count: {:10}'.format(
                'Ycppcnpc_MD_cCATALOGUE_CONTENT',
                fit_Ycppcnpc_MD_cCATALOGUE_CONTENT,
                count_Ycppcnpc_MD_cCATALOGUE_CONTENT))
            print ('{:<30} - fit: {:>10} count: {:10}'.format(
                'num_num',
                fit_num_num,
                count_num_num))
            print ('{:<30} - fit: {:>10} count: {:10}'.format(
                'GB_4_num',
                fit_GB_4_num,
                count_GB_4_num))
            print ('{:<30} - fit: {:>10} count: {:10}'.format(
                'GB_num',
                fit_GB_num,
                count_GB_num))
            print ('{:<30} - fit: {:>10} count: {:10}'.format(
                'Ycppccnpc_GB_num',
                fit_Ycppccnpc_GB_num,
                count_Ycppccnpc_GB_num))
            print ('{:<30} - fit: {:>10} count: {:10}'.format(
                'blog_article_num',
                fit_blog_article_num,
                count_blog_article_num))
            print()

    print ('Fit: {} / {} = {}%'.format(
        fit_sum, i, round(fit_sum/i*100, 2)))
    print ('Count: {} / {} = {}%'.format(
        count_sum, i, round(count_sum/i*100, 2)))
    print ('Filtered: {} / {} = {}%'.format(
        count_filtered, i, round(count_filtered/i*100, 2)))

    print ('{:<30} - fit: {:>10} count: {:10}'.format(
        'Y_MD_cCATALOGUE_CONTENT',
        fit_Y_MD_cCATALOGUE_CONTENT,
        count_Y_MD_cCATALOGUE_CONTENT))
    print ('{:<30} - fit: {:>10} count: {:10}'.format(
        'Ycppcnpc_MD_cCATALOGUE_CONTENT',
        fit_Ycppcnpc_MD_cCATALOGUE_CONTENT,
        count_Ycppcnpc_MD_cCATALOGUE_CONTENT))
    print ('{:<30} - fit: {:>10} count: {:10}'.format(
        'num_num',
        fit_num_num,
        count_num_num))
    print ('{:<30} - fit: {:>10} count: {:10}'.format(
        'GB_4_num',
        fit_GB_4_num,
        count_GB_4_num))
    print ('{:<30} - fit: {:>10} count: {:10}'.format(
        'GB_num',
        fit_GB_num,
        count_GB_num))
    print ('{:<30} - fit: {:>10} count: {:10}'.format(
        'Ycppccnpc_GB_num',
        fit_Ycppccnpc_GB_num,
        count_Ycppccnpc_GB_num))
    print ('{:<30} - fit: {:>10} count: {:10}'.format(
        'blog_article_num',
        fit_blog_article_num,
        count_blog_article_num))

def filter_pages(_link):
    "_"
    #print (_link)
    if re.search(r'http://blog.people.com.cn/open/articleFine', _link) or \
       _link.endswith('/index.html') or \
       _link.strip('/').endswith('.com.cn') or \
       '/bbs/' in _link or '/bbs_' in _link:
        return True
    #'http://world.people.com.cn/n/'
    #'http://cppcc.people.com.cn/n/'
    #'http://legal.people.com.cn/n/'
    #'http://pic.people.com.cn/n/'
    #'http://world.people.com.cn/GB/'
    #'http://society.people.com.cn/'
    #'http://cppcc.people.com.cn/GB/'
    #'http://npc.people.com.cn/n/'
    if _link.endswith('http://lianghui.people.com.cn/'):
        return True
