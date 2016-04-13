from archiver import archiver

if __name__ == '__main__':
    archive = archiver.get_archive_urls(
        from_date = '2016-04-01',
        earliest_date='2012-02-06',
        schema = 'http://politics.people.com.cn/GB/70731/review/{}.html')
    dearch = archiver.Dearchiver()
    #archive

    #dearch.clean()
    try:
        dearch.load_archive(archive)
    except httplib.IncompleteRead as e:
        print (e.partial)

    #dearch.find_links_in_archive()
    #print( len(dearch.archive_meta))
