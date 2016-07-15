"_"
import re

from collections import defaultdict as dd
def analyze_coverage(_data, names_and_funcs, all_links):
    "_"
    def show(j, fit_sum, count_sum, count_filtered, names_and_counts):
        "Print info"
        print ('Fit:      {:>5} / {:<5} = {:>5}%'.format(
            fit_sum, j, round(fit_sum/j*100, 2)))
        print ('Count:    {:>5} / {:<5} = {:>5}%'.format(
            count_sum, j, round(count_sum/j*100, 2)))
        print ('Filtered: {:>5} / {:<5} = {:>5}%'.format(
            count_filtered, j, round(count_filtered/j*100, 2)))
        for name, counts in names_and_counts.items():
            print ('{:<30} - fit: {:>10} count: {:10}'.format(
                name, counts['fit'], counts['count']))
    fit_sum = 0
    count_sum = 0
    count_filtered = 0
    names_and_counts = dd(lambda:dd(int))
    for _j, _link in enumerate(all_links):#[:3]:
        j = _j+1
        local = {}
        if (filter_pages(_link)) is True:
            count_filtered += 1
        for name, func in names_and_funcs:
            _result = func(_link, _data)
            local[name] = {
                'fit': int(_result is not False),
                'count': int(_result not in [None, False])
            }
            names_and_counts[name]['count'] += local[name]['count']
            names_and_counts[name]['fit'] += local[name]['fit']
        fit_sum += int(sum([v['fit'] for v in local.values()]) != 0)
        count_sum += int(sum([v['count'] for v in local.values()]) != 0)
        if j % 10000 == 0:
            print (40*'-=')
            show(j, fit_sum, count_sum, count_filtered, names_and_counts)
    show(j, fit_sum, count_sum, count_filtered, names_and_counts)

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
