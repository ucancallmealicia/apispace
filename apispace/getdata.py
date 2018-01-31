#/usr/bin/python3
#~/anaconda3/bin/python

import requests
import json
import csv
from apispace import admin

#also must figure out if these return actual values or just lists of IDs - probably the latter

global_record_types = ['agents/corporate_entities', 'agents/families', 'agents/people', 'agents/software', 'by-external-id', 'config/enumerations', 'container_profile',
                       'location_profiles', 'locations', 'permissions', 'reports', 'repositories', 'schemas', 'subjects', 'terms', 'users', 'users/complete'
                       'vocabularies']

repo_record_types = ['accessions', 'archival_objects', 'classification_terms', 'classifications', 'current_preferences', 'digital_object_components',
                     'digital_objects', 'events', 'groups', 'jobs', 'jobs/active', 'jobs/archived', 'jobs/import_types', 'preferences', 'rde_templates',
                     'resources', 'top_containers']

#make it so we can get a list based on URI?? I dunno, could add a million things.
#change name of output file...

#are there other configs I can join in with this?
def get_enumerations():
    values = admin.login()
    output = admin.opentxt()
    enumerations = requests.get(values[0] + '/config/enumerations?all_ids=true', headers=values[1]).json()
    json.dump(enumerations, output, indent=4, separators=(',', ':'))
    output.close()

#change this back to original....just added it to get dos....do this tomorrow in PROD; also should figure out if I want the txt file names to change depending on what I'm doing
#can't remember what the original looked like, though..
def get_repo_json(record_type, repo_id):
    values = admin.login()
    output = admin.opentxt()
    get_ids = requests.get(values[0] + '/repositories/' + str(repo_id) + '/' + str(record_type) + '?all_ids=true', headers=values[1]).json()
#    print(get_ids)
    x = 0
    for i in get_ids:
        x = x + 1
        resource = requests.get(values[0] + '/repositories/' + str(repo_id) + '/' + str(record_type) + '/' + str(i), headers=values[1]).json()
        json.dump(resource, output, indent=4, separators=(',', ':'))
        print('Dumping ' + str(x) + ' of ' + str(len(get_ids)))
        output.close()

def get_global_json(record_type):
    values = admin.login()
    output = admin.opentxt()
    get_ids = requests.get(values[0] + '/' + str(record_type) + '?all_ids=true', headers=values[1]).json()
#    print(get_ids)
    x = 0
    for i in get_ids:
        x = x + 1
        resource = requests.get(values[0] + '/' + str(record_type) + '/' + str(i), headers=values[1]).json()
        json.dump(resource, output, indent=4, separators=(',', ':'))
        print('Dumping ' + str(x) + ' of ' + str(len(get_ids)))
    output.close()

def export_ead():
    return

# def get_ead(repo_id):
#     values = admin.login()
#     #do not use this - make a new text file script so that I can save multiples
#     output = admin.opentxt()
#     get_ids = requests.get(values[0] + '/repositories/' + str(repo_id) + '/resources?all_ids=true', headers=values[1]).json()
#     x = 0
#     for i in get_ids:
#         x = x + 1
#         resource = requests.get(values[0] + '/repositories/' + str(repo_id) + '/' + str(record_type) + '/' + str(i) + '.xml', headers=values[1], stream=True)
#         #add something new here - want the files to be named by the resource_id

#if you just want a list of IDs? Why would this be?
def get_repo_ids(record_type, repo_id):
    values = admin.login()
    output = admin.opentxt()
    get_ids = requests.get(values[0] + '/repositories/' + str(repo_id) + '/' + str(record_type) + '?all_ids=true', headers=values[1]).json()
    output.write(get_ids)
    
def get_global_ids(record_type):
    values = admin.login()
    output = admin.opentxt()
    get_ids = requests.get(values[0] + '/' + str(record_type) + '?all_ids=true', headers=values[1]).json()
    output.write(get_ids)


# def get_data_from_list():
#     values = admin.login()
#     csvfile = admin.opencsv()
# #    output = admin.opentxt()
# #    csvoutfile = admin.opencsvout()
#     for row in csvfile:
#         ao_uri = row[0]
# #        tc_uri = row[1]
#         ao_json = requests.get(values[0] + ao_uri, headers=values[1]).json()
#         for key, value in ao_json.items():
#             if key == 'title':
#                 print(value)
#             if key == 'notes':
#                 for note in value:
#                     for subkey, subvalue in note.items():
#                         if subvalue == 'accessrestrict':
#                             print(note['subnotes'][0]['content'])
#        output.write(str(ao_json))
#         tc_json = requests.get(values[0] + tc_uri, headers=values[1]).json()
#         for key, value in tc_json.items():
#             if key == 'active_restrictions':
#                 for member in value:
#                     for subkey, subvalue in member.items():
#                         newlist = [subkey, subvalue]
#                         row.append(newlist)
#         csvoutfile.writerow(row)
            
#change to have repo num and note type in argument?
def get_note_ids():
    cursor = admin.login_db()
    #perhaps change these to be arguments...there are a few other things to fix too.
    note_type = input('Please enter the type of resource-level note to search: ')
    repository_num = input('Please enter your repository number: ')
    #create list from ead ids in text file
    outfile = input('Please enter path to input EAD list: ')
    eadlist = open(outfile, 'r')
    eadlisty = eadlist.read().split('\n')
    #sometimes a newline gets stuck in there - this takes care of that
    if eadlisty[-1] == '':
        del eadlisty[-1]
    moveon = input('Please press enter to run query...')
    print(moveon)
    #text file to store eads that don't have notes of the selected type attached
    textfile = input('Please enter path to output text file: ')
    output = open(textfile, 'a')
    #CSV file to store query data
    csvfile = input('Please enter path to output CSV: ')
    #needs headers in output CSV
    for ead in eadlisty:
        print('querying ' + ead)
        cursor.execute("""
        SELECT DISTINCT resource.ead_id AS EAD_ID
            , resource.identifier AS Identifier
            , resource.title AS Resource_Title
            , ev.value AS Level
            , CAST(note.notes as CHAR (20000) CHARACTER SET UTF8) AS Note_Text
            , CONCAT('/repositories/', resource.repo_id, '/resources/', resource.id) AS Resource_URL
            , note_persistent_id.persistent_id AS Persistent_ID
        FROM note
        LEFT JOIN note_persistent_id on note_persistent_id.note_id = note.id
        LEFT JOIN resource on note.resource_id = resource.id
        LEFT JOIN enumeration_value ev on ev.id = resource.level_id
        WHERE resource.repo_id = """ + repository_num + """ 
        AND note.notes LIKE '%""" + note_type + """%'
        AND resource.ead_id LIKE '%""" + ead + """%'""")
        #add columns later...
#        columns = cursor.description
        result = cursor.fetchall()
        #if no results, write ead id to text file
        if not cursor.rowcount:
            print('No results found for: ' + ead)
            output.write(ead + '\n')
        #if results, write to CSV
        else:
            for row in result:
                print(row)
                with open(csvfile, 'a', encoding='utf-8', newline='') as c:
                    writer = csv.writer(c)
                    writer.writerows([row])
    output.close()
    cursor.close()

def get_uris():
    cursor = admin.login_db()
    #perhaps change these to be arguments...there are a few other things to fix too.
    note_type = input('Please enter the type of resource-level note to search: ')
    repository_num = input('Please enter your repository number: ')
    #create list from ead ids in text file
    outfile = input('Please enter path to input EAD list: ')
    eadlist = open(outfile, 'r')
    eadlisty = eadlist.read().split('\n')
    #sometimes a newline gets stuck in there - this takes care of that
    if eadlisty[-1] == '':
        del eadlisty[-1]
    moveon = input('Please press enter to run query...')
    print(moveon)
    #text file to store eads that don't have notes of the selected type attached
    textfile = input('Please enter path to output text file: ')
    output = open(textfile, 'a')
    #CSV file to store query data
    csvfile = input('Please enter path to output CSV: ')
    #needs headers in output CSV
    for ead in eadlisty:
        print('querying ' + ead)
        cursor.execute("""
        SELECT resource.ead_id AS EAD_ID
            , resource.identifier AS Identifier
            , resource.title AS Resource_Title
#            , ev.value AS Level
#            , CAST(note.notes as CHAR (20000) CHARACTER SET UTF8) AS Note_Text
            , CONCAT('/repositories/', resource.repo_id, '/resources/', resource.id) AS Resource_URL
#            , note_persistent_id.persistent_id AS Persistent_ID
        FROM resource
#        LEFT JOIN note_persistent_id on note_persistent_id.note_id = note.id
#        LEFT JOIN resource on note.resource_id = resource.id
#        LEFT JOIN enumeration_value ev on ev.id = resource.level_id
        WHERE resource.repo_id = """ + repository_num + """ 
#        AND note.notes LIKE '%""" + note_type + """%'
        AND resource.ead_id LIKE '""" + ead + """'""")
        #add columns later...
#        columns = cursor.description
        result = cursor.fetchall()
        #if no results, write ead id to text file
        if not cursor.rowcount:
            print('No results found for: ' + ead)
            output.write(ead + '\n')
        #if results, write to CSV
        else:
            for row in result:
                print(row)
                with open(csvfile, 'a', encoding='utf-8', newline='') as c:
                    writer = csv.writer(c)
                    writer.writerows([row])
    output.close()
    cursor.close()

#def replace_note_by_type():

#def get_resource_dates():

#def get_resource_extents():
        
#do I want this for just one collection at a time or for many? Or for a list? I kind of think just one
#def get_aos(ead_id):
#    cursor = admin.login_db()
#    cursor.execute("""""")
#    columns = cursor.description
#    result = cursor.fetchall

#Should this be a SQL query? Already have something that gets the JSON, but I'd like a report that gets URIs...
#def get_dos():
#    cursor = admin.login_db()

