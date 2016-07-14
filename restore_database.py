"""Restore meta-data from raw html.

"""
import os

from restore import match_Y_MD_cCATALOGUE_CONTENT, match_num_num,\
        match_GB_4_num, match_GB_num, match_Ycppccnpc_GB_num,\
        match_blog_article_num, match_Ycppcnpc_MD_cCATALOGUE_CONTENT
#match_GB_shizheng, match_GB_num_review_num

from restore import analyze_coverage

from restore import get_mapping, get_page_data, get_all_links

names_and_funcs = (
    ('Y_MD_cCATALOGUE_CONTENT', match_Y_MD_cCATALOGUE_CONTENT),
    ('Ycppcnpc_MD_cCATALOGUE_CONTENT', match_Ycppcnpc_MD_cCATALOGUE_CONTENT),
    ('num_num', match_num_num),
    ('GB_4_num', match_GB_4_num),
    ('GB_num', match_GB_num),
    ('Ycppccnpc_GB_num', match_Ycppccnpc_GB_num),
    ('blog_article_num', match_blog_article_num))

PATH = '/Users/Lasper/safe data/_data_dearchiver/2_articles/'
RESTORE_PATH = 'data_restore'
os.makedirs(RESTORE_PATH, exist_ok=True)

page_data, missing_data = get_page_data(PATH, RESTORE_PATH)
all_links = get_all_links(RESTORE_PATH)
print ('all_links:      ', len(all_links))
print ('missing_data:   ', len(missing_data))
print ('page_data:      ', len(page_data))

mapping = get_mapping(all_links, page_data, names_and_funcs, RESTORE_PATH)

analyze_coverage(page_data, names_and_funcs, all_links)
