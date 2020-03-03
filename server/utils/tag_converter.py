#
# File: tag_converter.py
# Copyright: Grimm Project, Ren Pin NGO, all rights reserved.
# License: MIT
# -------------------------------------------------------------------------
# Authors:  Albert Yang(alberyan@cisco.com)
#
# Description: do tag conversion between string and array.
#
# To-Dos:
#
# Issues:
#   No issue so far.
#
# Revision History (Date, Editor, Description):
# 
#

import server.core.db as db
from server import admin_logger
from server.core.globals import TAG_LIST

'''Simple list version'''
def convert_ids_to_tags(ids):
    tag_list = []
    if not ids:
        return tag_list
    for id in ids.split(','):
        if not id or int(id) not in range(6):
            continue
        tag_list.append(TAG_LIST[int(id)])
    return tag_list

def convert_tags_to_ids(tags_list):
    if not tags_list:
        return ''
    id_list = []
    for tag in tags_list:
        if not tag or tag not in TAG_LIST:
            continue
        id_list.append(TAG_LIST.index(tag))
    return ','.join(id_list)

def get_all_tags():
    return TAG_LIST

'''DB version'''
def convert_ids_to_tags_db(ids):
    tag_list = []
    if not ids:
        return tag_list
    tags_map = get_tags_map_db()
    for id in ids.split(','):
        if not id or id not in tags_map:
            continue
        tag_list.append(tags_map[id])
    return tag_list

def convert_tags_to_ids_db(tags_list):
    if not tags_list:
        return ''
    id_list = []
    reverse_tags_map = get_reverse_tags_map_db()
    for tag in tags_list:
        if not tag or tag not in reverse_tags_map:
            continue
        id_list.append(reverse_tags_map[tag])
    return ','.join(id_list)

def get_tags_map_db():
    try:
        tags_table = db.expr_query('activity_tag')
    except:
        admin_logger.warning('get activity tag failed')
    tags_map = {}
    for tag in tags_table:
        tags_map[str(tag['tag_id'])] = tag['tag_name']
    return tags_map

def get_reverse_tags_map_db():
    try:
        tags_table = db.expr_query('activity_tag')
    except:
        admin_logger.warning('get activity tag failed')
    reverse_tags_map = {}
    for tag in tags_table:
        reverse_tags_map[tag['tag_name']] = str(tag['tag_id'])
    return reverse_tags_map

def get_all_tags_db():
    try:
        tags_info = db.expr_query('activity_tag')
    except:
        admin_logger.error('Critical: database query failed !')
    tags_list = []
    for tag in tags_info:
        tags_list.append(tag['tag_name'])
    return tags_list
