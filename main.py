from archiver import archiver

if __name__ == '__main__':
    archive = archiver.get_archive_urls(
        from_date = '2016-04-01',
        earliest_date='2012-02-06',
        schema = 'http://politics.people.com.cn/GB/70731/review/{}.html')
    dearch = archiver.Dearchiver()

    #dearch.clean()
    #dearch.load_data_files(silent = silent)
    #try:
    #    dearch.load_archive(archive)
    #except httplib.IncompleteRead as e:
    #    print (e.partial)

    #dearch.find_links_in_archive(
    #    target_element = 'ul', target_class = 'list_16')

    c = dearch.count_links()

    def stripper(href):
        return href.strip().replace('GB/index.html','').strip('/')

    c = {href:count for href, count in c.items()
                if not (stripper(href).split('.')[-1] in ['cn', 'com', ''])}

    dearch.show_counter(counter = c, root = 'http://politics.people.com.cn')
