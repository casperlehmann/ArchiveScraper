"""Output database entries for manual inspection.
"""

import sqlite3 as lite

with lite.connect('data/db') as con:
    cur = con.cursor()
    #cur.execute(
    #    'SELECT file_names.url FROM file_names JOIN links '
    #    'ON file_names.url = links.link ')
    #print (cur.fetchall())

    #cur.execute('SELECT file_names.url FROM file_names')
    #print (cur.fetchall())

    #cur.execute('SELECT link FROM links')
    #print (cur.fetchall())

    fn = cur.execute('SELECT COUNT(*) FROM file_names').fetchall()[0][0]
    l = cur.execute('SELECT COUNT(*) FROM links').fetchall()[0][0]
    j = cur.execute(
        'SELECT COUNT(*) FROM file_names JOIN links '
        'ON file_names.url = links.link').fetchall()[0][0]
    sj = cur.execute(
        'SELECT COUNT(*) FROM file_names JOIN links '
        'ON file_names.url = links.link WHERE links.url = "seed" ').fetchall()[0][0]
    nsj = cur.execute(
        'SELECT COUNT(*) FROM file_names JOIN links '
        'ON file_names.url = links.link WHERE links.url != "seed" ').fetchall()[0][0]

    fof = cur.execute(
        'SELECT COUNT(*) FROM file_names JOIN links '
        'ON file_names.url = links.link WHERE links.url != "seed" '
        'AND four_o_four = 1').fetchall()[0][0]

    nfof = cur.execute(
        'SELECT COUNT(*) FROM file_names JOIN links '
        'ON file_names.url = links.link WHERE links.url != "seed" '
        'AND four_o_four = 0').fetchall()[0][0]

    fetch = cur.execute(
        'SELECT COUNT(*) FROM file_names JOIN links '
        'ON file_names.url = links.link WHERE links.url != "seed" '
        'AND fetched = 1').fetchall()[0][0]
    non_fetch = cur.execute(
        'SELECT COUNT(*) FROM file_names JOIN links '
        'ON file_names.url = links.link WHERE links.url != "seed" '
        'AND fetched = 0').fetchall()[0][0]

    fof_fetch = cur.execute(
        'SELECT COUNT(*) FROM file_names JOIN links '
        'ON file_names.url = links.link WHERE links.url != "seed" '
        'AND four_o_four = 1 AND fetched = 1').fetchall()[0][0]
    fof_non_fetched = cur.execute(
        'SELECT COUNT(*) FROM file_names JOIN links '
        'ON file_names.url = links.link WHERE links.url != "seed" '
        'AND four_o_four = 1 AND fetched = 0').fetchall()[0][0]
    non_fof_fetched = cur.execute(
        'SELECT COUNT(*) FROM file_names JOIN links '
        'ON file_names.url = links.link WHERE links.url != "seed" '
        'AND four_o_four = 0 AND fetched = 1').fetchall()[0][0]
    non_fof_non_fetch = cur.execute(
        'SELECT COUNT(*)  FROM file_names JOIN links '
        'ON file_names.url = links.link WHERE links.url != "seed" '
        'AND four_o_four = 0 AND fetched = 0').fetchall()[0][0]

    print ('Count filenames:        {:>8}'.format(fn))
    print ('Count links:            {:>8}'.format(l))
    print ('Count JOINS:            {:>8}'.format(j))
    print ('Non-seed joins:         {:>8}'.format(nsj))
    print ('seed joins:             {:>8}'.format(sj))
    print ()
    print ('404:                    {:>8}'.format(fof))
    print ('Non-404:                {:>8}'.format(nfof))
    print ('fetched:                {:>8}'.format(fetch))
    print ('Non-fetched:            {:>8}'.format(non_fetch))
    print ()
    print ('404-fetched:            {:>8}'.format(fof_fetch))
    print ('404, Non-fetched        {:>8}'.format(fof_non_fetched))
    print ('Non-404,fetched         {:>8}'.format(non_fof_fetched))
    print ('Non-404, Non-fetched:   {:>8}'.format(non_fof_non_fetch))

