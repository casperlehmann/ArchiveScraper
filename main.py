from archiver import archiver

if __name__ == '__main__':
    archive = archiver.get_archive_urls()
    dearch = archiver.Dearchiver(archive)
    dearch.find_links()
    print( len(dearch.archive_meta))
