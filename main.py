"""Generate archive urls, download archives, scan for links, download articles.

"""

from archiver import archiver, url_tools

CLEAN_ARCHIVE = True
SCAN_ARCHIVE = True
SCAN_ARTICLES = True

if __name__ == '__main__':
    all_urls = url_tools.get_archive_urls(
        from_date = '2016-04-01',
        earliest_date='2012-02-06',
        schema = 'http://politics.people.com.cn/GB/70731/review/{}.html')

    agent = archiver.Agent(
        naming_json_file = '1_archive.json', scanned_json_file = '1_scanned.json',
        archive_folder = '1_archive')

    if CLEAN_ARCHIVE:
        agent.clean()
        agent = archiver.Agent(
            naming_json_file = '1_archive.json', scanned_json_file = '1_scanned.json',
            archive_folder = '1_archive')

    if SCAN_ARCHIVE:
        agent.load_archive(all_urls)
        agent.find_links_in_archive(target_element = 'ul', target_class = 'list_16')

    if SCAN_ARTICLES:
        home = 'http://politics.people.com.cn'
        article_urls = set(
            [item if not item.startswith('/') else home + item
             for url, li in agent.scanned_file_data.items()
             for item in li])

        reader = archiver.Agent(
            naming_json_file = '2_article.json', scanned_json_file = '2_artscan.json',
            archive_folder = '2_articles')
        print ('Fetching {} articles.'.format(len(article_urls)))
        reader.load_archive(article_urls)

    #for x in article_urls: print (x)
    #c = agent.count_links()

    #def stripper(href):
    #    return href.strip().replace('GB/index.html','').strip('/')

    #c = {href:count for href, count in c.items()
    #            if not (stripper(href).split('.')[-1] in ['cn', 'com', ''])}

    #agent.show_counter(counter = c, root = 'http://politics.people.com.cn')
