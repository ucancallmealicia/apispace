#/usr/bin/python3
#~/anaconda3/bin/python

import requests
import json
#import csv
from apispace import admin
#import pymysql


def create_agent():
    return

def update_agent():
    return

def update_agent_component():
    return

#links an agent of any type to a descriptive module of any type
def link_agent():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        agent_uri = row[0]
        description_uri = row[1]
        description_json = requests.get(values[0] + description_uri, headers=values[1]).json()
        description_json['linked_agents'].append({'ref': agent_uri})
        description_data = json.dumps(description_json)
        description_post = requests.post(values[0] + description_uri, headers=values[1], data=description_data).json()
        print(description_post)

def create_names():
    print('placeholder')
        
def get_agents():
    print('placeholder')
#    cursor = admin.login_db()

# def create_subject():
#     values = admin.login()
#     csvfile = admin.opencsv()
#     for row in csvfile:

#def update_subject():

#this could work for other modules; but tricky if there are, say, multiple dates
def update_subject_component():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        subject_uri = row[0]
        component_to_update = row[1]
        updated_text = row[2]
        subject_json = requests.get(values[0] + '/subjects/' + subject_uri, headers=values[1]).json()
        subject_json[component_to_update] = updated_text
        subject_data = json.dumps(subject_json)
        subject_update = requests.post(values[0] + subject_uri, headers=values[1], data=subject_data).json()
        print(subject_update)        
        
#def link_to_resource():
    
#def link_to_ao():
    
#def delete_subject():

#def get_subjects():
#    cursor = admin.login_db()