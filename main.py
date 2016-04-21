from archiver import archiver, date_tools, url_tools

# agent = archiver.Dearchiver()
# url_tools.get_archive_urls() | 

if __name__ == '__main__':
    all_urls = url_tools.get_archive_urls(
        from_date = '2016-04-01',
        earliest_date='2012-02-06',
        schema = 'http://politics.people.com.cn/GB/70731/review/{}.html')

    agent = archiver.Agent(
        naming_json_file = 'archive.json', scanned_json_file = 'scanned.json')

    #agent.clean()
    #agent = archiver.Agent(
    #    naming_json_file = 'archive.json', scanned_json_file = 'scanned.json')

    agent.load_archive(all_urls)
    agent.find_links_in_archive(target_element = 'ul', target_class = 'list_16')

    c = agent.count_links()

    def stripper(href):
        return href.strip().replace('GB/index.html','').strip('/')

    c = {href:count for href, count in c.items()
                if not (stripper(href).split('.')[-1] in ['cn', 'com', ''])}

    agent.show_counter(counter = c, root = 'http://politics.people.com.cn')
