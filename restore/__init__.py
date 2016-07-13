"""Module for restoring database file.
"""
from restore.match import match_Y_MD_cCATALOGUE_CONTENT, match_num_num,\
        match_GB_4_num, match_GB_shizheng, match_GB_num_review_num, \
        match_GB_num, match_Ycppccnpc_GB_num, match_blog_article_num, \
        match_Ycppcnpc_MD_cCATALOGUE_CONTENT, match, match_content_id

from restore.analyzer import analyze_coverage

from restore.page_handler import page_identifier, page_mapper, page_contains_url

from restore.data_handler import get_mapping, get_page_data, get_all_links
