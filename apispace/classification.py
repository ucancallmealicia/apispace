#/usr/bin/python3
#~/anaconda3/bin/python

import requests
import json
import csv
from apispace import admin
#import pymysql

#I think it would be possible to combine all of this into a single function...like "if classification not in" and "if parent not in", etc.

#should work but haven't tested - it is easier to create these manually unless you're doing more than one top level at a time
def create_top_level():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        identifier = row[0]
        title = row[1]
        description = row[2]
        repository = row[3]
        new_class_term = {"identifier": identifier, "title": title, "description": description, "publish": True,
                          "repository": {'ref': repository}}
        new_class_json = json.dumps(new_class_term)
        new_class_post = requests.post(values[0] + '/repositories/12/classifications', headers=values[1], data=new_class_json).json()
        print(new_class_post)

#this one should be the same as top level but with a Classification column; should not have a parent column
def create_sub_level():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        identifier = row[0]
        title = row[1]
        description = row[2]
        repository = row[3]
        classification = row[4]
        new_class_term = {"identifier": identifier, "title": title, "description": description, "publish": True,
                          "repository": {'ref': repository}, "classification": {'ref': classification}}
        new_class_json = json.dumps(new_class_term)
        new_class_post = requests.post(values[0] + '/repositories/12/classification_terms', headers=values[1], data=new_class_json).json()
        print(new_class_post)

def create_sub_sub_level():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        identifier = row[0]
        title = row[1]
        description = row[2]
        repository = row[3]
        classification = row[4]
        parent = row[5]
        new_class_term = {"identifier": identifier, "title": title, "description": description, "publish": True,
                          "repository": {'ref': repository}, "classification": {'ref': classification}, "parent": {'ref': parent}}
        new_class_json = json.dumps(new_class_term)
        new_class_post = requests.post(values[0] + '/repositories/12/classification_terms', headers=values[1], data=new_class_json).json()
        print(new_class_post)

def link_records():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        classification = row[0]
        record = row[1]
        new_rec_link = requests.get(values[0] + classification, headers=values[1]).json()
        new_rec_link['linked_records'].append({'ref': record})
        print(new_rec_link)
        new_link_json = json.dumps(new_rec_link)
        new_link_post = requests.post(values[0] + classification, headers=values[1], data=new_link_json).json()
        print(new_link_post)

def get_class_uris():
    cursor = admin.login_db()
    identifier = input('Please enter classification identifier (i.e. YRG): ')
    csvfile = input('Please enter path to output CSV: ')
    cursor.execute("""
    SELECT title
        , identifier
        , description
        , parent_name
        , CONCAT('/repositories/12/classification_terms/', id) AS URI
    FROM classification_term
    WHERE identifier like '%""" + identifier + """%'""")
    result = cursor.fetchall()
    for row in result:
        print(row)
        with open(csvfile, 'a', newline='') as c:
            writer = csv.writer(c)
            writer.writerows([row])
    cursor.close()
    
def get_class_rec_links():
    cursor = admin.login_db()
    identifier = input('Please enter classification identifier (i.e. YRG): ')
    csvfile = input('Please enter path to output CSV: ')
    cursor.execute("""
    SELECT ct.identifier AS classification_identifier
        , ct.title AS classification_title
        , resource.identifier AS resource_identifier
        , resource.title AS resource_title
        , CONCAT('/repositories/12/classification_terms/', ct.id) AS classification_URI
        , CONCAT('/repositories/12/resources', resource.id) AS resource_URI
    FROM classification_term ct
    LEFT JOIN classification_rlshp cr on cr.classification_term_id = ct.id
    LEFT JOIN resource on resource.id = cr.resource_id
    WHERE ct.identifier like '%""" + identifier + """%'""")
    result = cursor.fetchall()
    for row in result:
        print(row)
        with open(csvfile, 'a', newline='') as c:
            writer = csv.writer(c)
            writer.writerows([row])
    cursor.close()

'''endpoints for classifications:
 "parent": {'ref': parent}

This is a classification term that falls right below the top-level classification (i.e. the YRG 01-50)
{'lock_version': 0,
'identifier': 'RG 0001.0001',
'title': 'Test_Class_Term',
'description': 'Test classification term',
'position': 0,
'created_by': 'amd243',
'last_modified_by': 'amd243',
'create_time': '2017-07-10T13:17:57Z',
'system_mtime': '2017-07-10T13:18:06Z',
'user_mtime': '2017-07-10T13:17:57Z',
'jsonmodel_type': 'classification_term',
'publish': True,
'path_from_root': [{'title': 'Test_Class', 'identifier': 'RG 0001'},
    {'title': 'Test_Class_Term', 'identifier': 'RG 0001.0001'}],
'linked_records': [],
'uri': '/repositories/12/classification_terms/1',
'repository': {'ref': '/repositories/12'},
'creator': {'ref': '/agents/people/39276'},
'classification': {'ref': '/repositories/12/classifications/1'}}

This is a classification term that has a parent...either the subclass or subsubclass
{'lock_version': 0,
'identifier': 'RG.0001.0002.0001',
'title': 'Test_Class_Other_Sub_Term',
'description': 'Other subclassification term',
'position': 0,
'created_by': 'amd243',
'last_modified_by': 'amd243',
'create_time': '2017-07-10T13:19:30Z',
'system_mtime': '2017-07-10T13:19:30Z',
'user_mtime': '2017-07-10T13:19:30Z',
'jsonmodel_type': 'classification_term',
'publish': True, '
path_from_root': [{'title': 'Test_Class', 'identifier': 'RG 0001'},
    {'title': 'Test_Class_Other_Term', 'identifier': 'RG 0001.0002'},
    {'title': 'Test_Class_Other_Sub_Term', 'identifier': 'RG.0001.0002.0001'}],
'linked_records': [],
'uri': '/repositories/12/classification_terms/4',
'repository': {'ref': '/repositories/12'},
'creator': {'ref': '/agents/people/39276'},
'classification': {'ref': '/repositories/12/classifications/1'},
'parent': {'ref': '/repositories/12/classification_terms/3'}}

repositories/12/classifications - creates a top-level classification - better to do this manually I think.
{'create_time': '2017-07-10T13:11:37Z',
 'created_by': 'amd243',
 'creator': {'ref': '/agents/people/39276'},
 'description': 'Test classification',
 'identifier': 'RG 0001',
 'jsonmodel_type': 'classification',
 'last_modified_by': 'amd243',
 'linked_records': [],
 'lock_version': 1,
 'path_from_root': [{'identifier': 'RG 0001', 'title': 'Test_Class'}],
 'publish': True,
 'repository': {'ref': '/repositories/12'},
 'system_mtime': '2017-07-10T13:18:06Z',
 'title': 'Test_Class',
 'uri': '/repositories/12/classifications/1',
 'user_mtime': '2017-07-10T13:18:06Z'}
 
 yrg_csv = 'C:\\Users\\amd243\\Desktop\\Scripting_Tasks\\Classifications\\yrg_sub_classifications.csv'

 '''




