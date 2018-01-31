#/usr/bin/python3
#~/anaconda3/bin/python

#record types: accession, archival object, digital object, digital object component, repository, resource

import requests
import json
#import csv
#import pymysql
from apispace import admin
from apispace import schema
#from apispace import config
import time
import pprint

'''
To-Do:
-Add 'jsonmodel_type' to all functions if missing
-Add outfiles as needed
-Timekeeping '''

##################### FUNCTIONS #####################

'''
The create_records function can theoretically be used to create any top-level record (i.e. repo, accession, resource, archival 
object, etc. In the current setup it takes as arguments string representations of the jsonmodel type (usually singular - i.e. 
'resource', 'accession', 'archival_object') and any desired subrecords (usually plural - i.e. 'dates, 'extents', 
'file_versions'). You currently have to type in each subrecord you want - I will hopefully get a better solution for this
eventually. I was thinking about looking up the values in the schema and getting their keys, but there are some
values which are repeated across different schemas, but have different properties.

As input, the function takes a CSV. The CSV can have a variable number of columns depending on what info the user
wishes to add. It must have the repository URI - the function looks for the column header 'repo_uri', but this could
probably be changed. All of the other column headers must match the keys in the ArchivesSpace JSONModel. The templates
module should make adhering to this structure a little easier

The function pulls in info from the schema submodule, which is derived from the ArchivesSpace schema (still need to test
pulling this in from the API. My work on the schema part is incomplete, but I have been able to successfully create
records with this function. I also am quite sure there is a better way to get the data I need from the schema,
but at this point I was just seeing if my idea could work.

A potential downside of this approach is that the more schema-specific aspects of the schema manipulation I did may
not work on all past or future versions of AS. However, the schema should be relatively stable in structure for the time being
until I can figure out a more abstracted approach

'''

#still need to add something that checks if the row is empty
def create_records(jsonmodel_type, *subrecords):
    values = admin.login()
    csvfile = admin.opencsvdict()
    data_dict = schema.add_refs()
    #Loops through each file in the CSV
    for row in csvfile:
        new_record = {'jsonmodel_type': jsonmodel_type}
        for k, v in row.items():
            if k in data_dict[jsonmodel_type]:
                new_record[k] = v
        if 'publish' in row.keys():
            if row['publish'] == 'True':
                new_record['publish'] = True
            elif row['publish'] == 'False':
                new_record['publish'] = False
        newdict = dict.fromkeys(subrecords)
        for subrecord in subrecords:
            newdict[subrecord] = [{}]
            if subrecord in data_dict[jsonmodel_type]:
                print(data_dict[jsonmodel_type][subrecord])
                for key in data_dict[jsonmodel_type][subrecord].keys():
                    if key in row.keys():
                        for member in newdict[subrecord]:
                            member.update({key: row[key]})
        new_record.update(newdict)    
        pprint.pprint(new_record)
        record_data = json.dumps(new_record)
        record_create = requests.post(values[0] + row['repo_uri'] + '/' + jsonmodel_type + 's', headers=values[1], data=record_data).json()
        print(record_create)

def create_repositories():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        repo_name = row[0]
        record_json = {'repo_name': repo_name}
        record_data = json.dumps(record_json)
        record_update = requests.delete(values[0] + '/repositories', headers=values[1], data=record_data).json()
        print(record_update)

'''This function creates a base-level, bare-minimum accession record. Can update to add other parts - additional string-type 
#values, dates, extents, instances, etc. using other functions in this submodule'''
def create_accessions():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        repo_uri = row[0]
        identifier = row[1]
        title = row[2]
        accession_date = row[3]
        new_accession = {'id_0': identifier, 'title': title, 'accession_date': accession_date, 'repository': {'ref': repo_uri}, 
                         'jsonmodel_type': 'accession'}
        accession_data = json.dumps(new_accession)
        accession_create = requests.post(values[0] + repo_uri + '/accessions', headers=values[1], data=accession_data).json()
        print(accession_create)

'''This function creates a base-level, bare-minimum resource record. Can add more data using other functions in this module'''
def create_resources():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        repo_uri = row[0]
        identifier = row[1]
        title = row[2]
        language = row[3]
        level = row[4]
        begin_date = row[5]
        end_date = row[6]
        date_type = row[7]
        date_label = row[8]
        extent_type = row[9]
        extent_portion = row[10]
        extent_number = row[11]
        container_summary = row[12]
        new_resource = {'id_0': identifier, 'title': title, 'language': language, 'level': level,
                        'dates' : [{'begin': begin_date, 'end': end_date, 'date_type': date_type, 'label': date_label, 
                                    'jsonmodel_type': 'date'}],
                        'extents': [{'extent_type': extent_type, 'portion': extent_portion, 'number': extent_number, 
                                     'container_summary': container_summary, 'jsonmodel_type': 'extent'}], 
                        'repository': {'ref': repo_uri}, 'jsonmodel_type': 'resource'}
        resource_data = json.dumps(new_resource)
        print(resource_data)
        resource_create = requests.post(values[0] + repo_uri + '/resources', headers=values[1], data=resource_data).json()
        print(resource_create)
    
# This function creates a base-level, bare-minimum archival object, attached to a resource or other archival object. Can update
#to add other parts - additional string-type values, dates, extents, instances, etc. using other functions in this 
#submodule
#TEST this - is component id required only when a series uri is present?
def create_archival_objects():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        resource_uri = row[0]
        repo_uri = row[1]
        title = row[2]
        level = row[3]
        parent_series_uri = row[4]
        component_id = row[5]
        if parent_series_uri != '':
            new_ao = {'title': title, 'level': level, 'repository': {'ref': repo_uri},
                'resource': {'ref': resource_uri}, 'jsonmodel_type': 'archival_object'}
        else:
            new_ao = {'component_id': component_id, 'title': title, 'level': level, 
                      'repository': {'ref': repo_uri}, 'resource': {'ref': resource_uri}, 
                      'parent': {'ref': parent_series_uri}, 'jsonmodel_type': 'archival_object'}
        ao_data = json.dumps(new_ao)
        ao_create = requests.post(values[0] + repo_uri + '/archival_objects', headers=values[1], data=ao_data).json()
        print(ao_create)
        
# This function creates a base-level, bare-minimum digital object, attached to a resource or archival object. Can update
#to add other parts - additional string-type values, dates, extents, instances, etc. using other functions in this 
#submodule; add linked agents stuff later
def create_digital_objects():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        repo_uri = row[0]
        digital_object_id = row[1]
        title = row[2]
        new_do = {'digital_object_id': digital_object_id, 'jsonmodel_type': 'digital_object', 
                  'title': title, 'repository': {'ref': repo_uri}}
        do_data = json.dumps(new_do)
        do_create = requests.post(values[0] + repo_uri + '/digital_objects', headers=values[1], data=do_data).json()
        print(do_create)
        
#creates a digital object component record, attached to a parent digital object
def create_dig_object_components():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        repo_uri = row[0]
        parent_uri = row[1]
        component_id = row[2]
        title = row[3]
        new_doc = {'component_id': component_id, 'title': title, 'parent': {'ref': parent_uri},
                   'repository': {'ref': repo_uri}, 'jsonmodel_type': 'digital_object_component'}
        doc_data = json.dumps(new_doc)
        doc_create = requests.post(values[0] + repo_uri + '/digital_object_components', headers=values[1], data=doc_data).json()
        print(doc_create)

#may have to add a loop if there are multiple dates, extents, etc.; make sure users want to change all of them; also
#this doesn't support changing some components but not others - like the location coordinates but
#not the rest; could change one location coordinate...
#Creates a new date and appends it to a record
#Check to make sure that the "if dates = ''" is not necessary = can just append to empty list anyway
#Remove expression? Or add another if statement - sometimes an expression will be necessary
def create_dates():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        record_uri = row[0]
        begin_date = row[1]
        end_date = row[2]
        expression = row[3]
        date_type = row[4]
        label = row[5]
        record_json = requests.get(values[0] + record_uri, headers=values[1]).json()
        if date_type == 'single': 
            new_date = [{'begin': begin_date, 'date_type': 'single',
                            'expression': expression, 'jsonmodel_type': 'date',
                            'label': label}]
        else:         
            new_date = [{'begin': begin_date, 'end': end_date, 'date_type': date_type,
                            'expression': expression, 'jsonmodel_type': 'date',
                            'label': label}]
        record_json['dates'].append(new_date)
        record_data = json.dumps(record_json)
        record_update = requests.post(values[0] + record_uri, headers=values[1], data=record_data).json()
        print(record_update)

#Creates a new extent and adds it to an existing record. If no extents exist this will be the only one; if not
#it will be added to the extent list
#Add if statement for container summary?
def create_extents():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        record_uri = row[0]
        container_summary = row[1]
        extent_type = row[2]
        number = row[3]
        portion = row[4]
        record_json = requests.get(values[0] + record_uri, headers=values[1]).json()
        new_extent = {'container_summary': container_summary,
                  'extent_type': extent_type, 'jsonmodel_type': 'extent',
                  'number': number, 'portion': portion}
        record_json['extents'].append(new_extent)
        record_data = json.dumps(record_json)
        record_update = requests.post(values[0] + record_uri, headers=values[1], data=record_data).json()
        print(record_update)

def create_external_documents():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        record_uri = row[0]
        record_json = requests.get(values[0] + record_uri, headers=values[1]).json()
        new_ext_doc = {'jsonmodel_type': 'external_document'}
        record_json['external_documents'].append(new_ext_doc)
        record_data = json.dumps(record_json)
        record_update = requests.post(values[0] + record_uri, headers=values[1], data=record_data).json()
        print(record_update)

def create_external_ids():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        record_uri = row[0]
        record_json = requests.get(values[0] + record_uri, headers=values[1]).json()
        record_data = json.dumps(record_json)
        record_update = requests.post(values[0] + record_uri, headers=values[1], data=record_data).json()
        print(record_update)

def create_file_versions():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        record_uri = row[0]
        file_uri = row[1]
        identifier = row[2]
        record_json = requests.get(values[0] + record_uri, headers=values[1]).json()
        new_file_version = {'file_uri': file_uri, 'jsonmodel_type': 'file_version', 'identifier': identifier}
        record_json['file_versions'].append(new_file_version)
        record_data = json.dumps(record_json)
        record_update = requests.post(values[0] + record_uri, headers=values[1], data=record_data).json()
        print(record_update)

def create_revision_statements():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        record_uri = row[0]
        record_json = requests.get(values[0] + record_uri, headers=values[1]).json()
        record_data = json.dumps(record_json)
        record_update = requests.post(values[0] + record_uri, headers=values[1], data=record_data).json()
        print(record_update)

def create_singlepart_notes():
    values = admin.login()
    csvfile = admin.opencsv()
    txtfile = admin.opentxt()
    for row in csvfile:
        record_uri = row[0]
        note_text = row[1]
        note_type = row[2]
        record_json = requests.get(values[0] + record_uri, headers=values[1]).json()
        new_note = {'jsonmodel_type': 'note_singlepart', 'content': [note_text],
                    'type': note_type}
        record_json['notes'].append(new_note)
        record_data = json.dumps(record_json)
        record_update = requests.post(values[0] + record_uri, headers=values[1], data=record_data).json()
        admin.writetxt(txtfile, record_update)
        print(record_update)

#What if I want a multipart note with a different kind of text...
#have to change the pub status
def create_multipart_notes():
    values = admin.login()
    csvfile = admin.opencsv()
    txtfile = admin.opentxt()
    for row in csvfile:
        record_uri = row[0]
        note_text = row[1]
        note_type = row[2]
        record_json = requests.get(values[0] + record_uri, headers=values[1]).json()
        new_note = {"jsonmodel_type": "note_multipart", 
                    "subnotes": [{'content': note_text, 'jsonmodel_type': 'note_text', 'publish': True}], 
                    'type': note_type, 'publish': True}
        try:
            record_json['notes'].append(new_note)
        except:
            print('note did not append')
        record_data = json.dumps(record_json)
        record_update = requests.post(values[0] + record_uri, headers=values[1], data=record_data).json()
        admin.writetxt(txtfile, record_update)
        print(record_update)

#What happens if the rights_restriction key doesn't exist, like in the older access notes? Maybe have to
#post without making any changes so the structure changes? Test this.
def create_rights_restrictions():
    values = admin.login()
    csvfile = admin.opencsv()
    txtfile = admin.opentxt()
    for row in csvfile:
        record_uri = row[0]
        persistent_id = row[1]
        begin = row[2]
        end = row[3]
        local_type = row[4]
        note_type = row[5]
        record_json = requests.get(values[0] + record_uri, headers=values[1]).json()
        new_restriction = {'begin': begin, 'end': end, 'local_access_restriction_type': [local_type],
                           'restriction_note_type': note_type, 'jsonmodel_type': 'rights_restriction'}
        for note in record_json['notes']:
            if note['persistent_id'] == persistent_id:
                note['rights_restriction'] = new_restriction
        record_data = json.dumps(record_json)
        record_update = requests.post(values[0] + record_uri, headers=values[1], data=record_data).json()
        admin.writetxt(txtfile, record_update)
        print(record_update)

def create_note_bioghist():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        record_uri = row[0]
        record_json = requests.get(values[0] + record_uri, headers=values[1]).json()
        record_data = json.dumps(record_json)
        record_update = requests.post(values[0] + record_uri, headers=values[1], data=record_data).json()
        print(record_update)

def create_note_abstract():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        record_uri = row[0]
        record_json = requests.get(values[0] + record_uri, headers=values[1]).json()
        record_data = json.dumps(record_json)
        record_update = requests.post(values[0] + record_uri, headers=values[1], data=record_data).json()
        print(record_update)

def create_note_bibliography():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        record_uri = row[0]
        record_json = requests.get(values[0] + record_uri, headers=values[1]).json()
        record_data = json.dumps(record_json)
        record_update = requests.post(values[0] + record_uri, headers=values[1], data=record_data).json()
        print(record_update)

#Will update any single component, if the component to update is listed in column 2 of CSV
#could also have the component type as an argument, but this way allows for variable types of components - but why do you want that?          
def update_record_component():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        record_uri = row[0]
        component_to_update = row[1]
        updated_text = row[2]
        record_json = requests.get(values[0] + record_uri, headers=values[1]).json()
        record_json[component_to_update] = updated_text
        record_data = json.dumps(record_json)
        record_update = requests.post(values[0] + record_uri, headers=values[1], data=record_data).json()
        print(record_update)

#Works for all non-nested values/string values; updates a variable amount of fields depending on user
#input; can't update different fields for different records
#Fix this - don't need fieldlist, since it's already a list, right?
def update_record_components(*field):
    values = admin.login()
    csvfile = admin.opencsvdict()
    for row in csvfile:
        record_uri = row['uri']
        #Is this necessary? I don't remember why I added it
        fieldlist = field
        record_json = requests.get(values[0] + record_uri, headers=values[1]).json()
        for f in fieldlist:
            for key, value in row.items():
                #This checks to make sure that the function arguments match what is in the CSVdict key
                if f == key:
                    record_json[key] = value
        record_data = json.dumps(record_json)
        record_update = requests.post(values[0] + record_uri, headers=values[1], data=record_data).json()
        print(record_update)

#Pub status updates need their own function because they require conversion from string to Boolean values
#should work for all record types, but need to test this
def update_record_pub_status():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        record_uri = row[0]
        #1 for publish, 0 for unpublish
        updated_status = row[1]
        record_json = requests.get(values[0] + record_uri, headers=values[1]).json()
        if updated_status == '1':
            record_json['publish'] = True
        elif updated_status == '0':
            record_json['publish'] = False
        record_data = json.dumps(record_json)
        record_update = requests.post(values[0] + record_uri, headers=values[1], data=record_data).json()
        print(record_update)

#Can use this to update single parts of a date record; will update all dates in a single record as it loops through
def update_subrecord_component(subrecord, component):
    starttime = time.time()
    values = admin.login()
    csvfile = admin.opencsv()
    txtout = admin.opentxt()
    x = 0
    y = 0
    for row in csvfile:
        x = x + 1
        resource_uri = row[0]    
        updated_text = row[1]
        try:
            resource_json = requests.get(values[0] + resource_uri, headers=values[1]).json()
            #This doesn't need the position because it will update any value...careful!
            for date in resource_json[subrecord]:
                date[component] = updated_text
                resource_data = json.dumps(resource_json)
                resource_update = requests.post(values[0]+ resource_uri, headers=values[1], data=resource_data).json()
                print(resource_update)
                if 'status' in resource_update.keys():
                    y = y + 1
                if 'error' in resource_update.keys():
                    txtout.write('error: could not update ' + str(resource_uri) + '\n')
                    #this isn't working
                    txtout.write('log: ' + str(resource_update.get('error')) + '\n')
        except:
            txtout.write('could not locate object ' + str(resource_uri) + '\n')
            continue
    elapsedtime = time.time() - starttime
    m, s = divmod(elapsedtime, 60)
    h, m = divmod(m, 60)
    txtout.write('Total time elapsed: ')
    txtout.write('%d:%02d:%02d' % (h, m, s))
    txtout.write('\n' + 'Total update attempts: ' + str(x) + '\n')
    #add count of successful updates to log file
    txtout.write('Records updated successfully: ' + str(y) + '\n')
    txtout.close()

#Use this to update multiple parts of single subrecord; This will only act on a specific subrecord; it won't loop through
#and apply the same action to all subrecords (i.e. multiple dates in an archival object)
#Update sub_record_components without submodules - dates, extents, revision statements, file versions
#This will become much more useful once I submit the PR for subrecord IDs in JSON
# external ids, external documents
def update_subrecord_components(subrecord, *field):
    starttime = time.time()
    values = admin.login()
    csvfile = admin.opencsvdict()
    txtout = admin.opentxt()
    x = 0
    y = 0
    for row in csvfile:
        x = x + 1
        record_uri = row['uri']
        try:
            record_json = requests.get(values[0] + record_uri, headers=values[1]).json()
            for f in field:
                for key, value in row.items():
                    if f == key:
                        if key == 'repository':
                            record_json[subrecord][0][key] = {'ref': value}
                        else:
                            #this needs the position because it doesn't update every one, just the first.
                            #all the more reason we need IDs for this stuff.                                       
                            record_json[subrecord][0][key] = value
            record_data = json.dumps(record_json)
            record_update = requests.post(values[0] + record_uri, headers=values[1], data=record_data).json()
            print(record_update)
            if 'status' in record_update.keys():
                y = y + 1
            if 'error' in record_update.keys():
                txtout.write('error: could not update ' + str(record_uri) + '\n')
                txtout.write('log: ' + str(record_update.get('error')) + '\n')
        except:
            txtout.write('could not locate object ' + str(record_uri))
            continue            
    elapsedtime = time.time() - starttime
    m, s = divmod(elapsedtime, 60)
    h, m = divmod(m, 60)
    txtout.write('Total time elapsed: ')
    txtout.write('%d:%02d:%02d' % (h, m, s))
    txtout.write('\n' + 'Total update attempts: ' + str(x) + '\n')
    #add count of successful updates to log file
    txtout.write('Records updated successfully: ' + str(y) + '\n')
    txtout.close()

#Or could do update_note_component, as before. Or "update date component, etc."
#this was originally "update note publication status"
#check on this - it might not work...need to make sure if I'm updating content for multipart that it's nested
def update_note_component():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        resource_uri = row[0]
        component_to_update = row[1]
        update_text = row[2]
        resource_json = requests.get(values[0] + resource_uri, headers=values[1]).json()
        for note in resource_json['notes']:
            if note['jsonmodel_type'] == 'note_multipart':
                note['subnotes'][0][component_to_update] = update_text
            elif note['jsonmodel_type'] == 'note_singlepart':
                note[component_to_update] = [update_text]
        resource_data = json.dumps(resource_json)
        resource_update = requests.post(values[0] + resource_uri, headers=values[1], data=resource_data).json()
#        admin.writetxt(txtfile, resource_update)
        print(resource_update)

#uses persistent ID as key; can also do this for resource_level notes...or abstract and use for both.
def update_note_pub_status():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        uri = row[0]
        persistent_id = row[1]
        updated_status = row[2]
        json = requests.get(values[0] + uri, headers=values[1]).json()
        for note in json['notes']:
            if note['persistent_id'] == persistent_id:
                if updated_status == '1':
                    note['publish'] = True
                elif updated_status == '0':
                    note['publish'] = False
        data = json.dumps(json)
        ao_update = requests.post(values[0] + uri, headers=values[1], data=data).json()
        print(ao_update)

#test this - should write to output file now
def replace_note_by_id():
    #replaces a note's content in ArchivesSpace using a persistent ID
    values = admin.login()
    csvfile = admin.opencsv()
    txtfile = admin.opentxt()
    for row in csvfile:
        resource_uri = row[0]
        persistent_id = row[1]
        note_text = row[2]
        resource_json = requests.get(values[0] + resource_uri, headers=values[1]).json()
        for note in resource_json['notes']:
            if note['jsonmodel_type'] == 'note_multipart':
                if note['persistent_id'] == persistent_id:
                    note['subnotes'][0]['content'] = note_text
            elif note['jsonmodel_type'] == 'note_singlepart':
                if note['persistent_id'] == persistent_id:
                    note['content'] = [note_text]
        resource_data = json.dumps(resource_json)
        resource_update = requests.post(values[0] + resource_uri, headers=values[1], data=resource_data).json()
        admin.writetxt(txtfile, resource_update)
        print(resource_update)

def delete_notes():
    values = admin.login()
    csvfile = admin.opencsv()
    txtfile = admin.opentxt()
    for row in csvfile:
        resource_uri = row[0]
        persistent_id = row[1]
        resource_json = requests.get(values[0] + resource_uri, headers=values[1]).json()
        for key, valuelist in resource_json.items():
            if key == 'notes':
                for note in valuelist:
                    newdict = {k:v for k,v in note.items()}
                    for key, value in newdict.items():
                        if value == persistent_id:
                            note.clear()
        resource_data = json.dumps(resource_json)
        resource_update = requests.post(values[0] + resource_uri, headers=values[1], data=resource_data).json()
        admin.writetxt(txtfile, resource_update)
        print(resource_update)

#Delete a whole date record - see delete note test
def delete_subrecords():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        record_uri = row[0]
        record_json = requests.get(values[0] + record_uri, headers=values[1]).json()
        record_data = json.dumps(record_json)
        record_update = requests.delete(values[0] + record_uri, headers=values[1], data=record_data).json()
        print(record_update)

#Delete part of a date record
def delete_subrecord_components():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        record_uri = row[0]
        record_json = requests.get(values[0] + record_uri, headers=values[1]).json()
        record_data = json.dumps(record_json)
        record_update = requests.delete(values[0] + record_uri, headers=values[1], data=record_data).json()
        print(record_update)

#NOTE FROM SLACK LIST: batch deleting digital objects through the API seems to delete digital object records from the 'digital_object" table 
#in the database, but retain digital object instances in the 'instance' table and corresponding records in the 'instance_do_link_rlshp' 
#table.  If the deleted digital object instance is the first instance linked to an archival object, then that archival object 
#is wrecked (not retrievable through the staff UI or API, presumably because the JSON is malformed?). So, essentially, you'd need 
#to delete the DO instance first, and then the actual DO.

#This function removes digital object instances from an archival object record. If no digital object URI is provided it will loop
#through all instances and delete all digital object instances; if a URI is provided it will delete the instance linked to that URI
#only. This does not delete the digital objects themselves, but only the instances; if digital objects actually need to go, use
#the delete_do function; BUT, per the Slack channel, it is necessary to delete any instances linked to DOs before deleting the actual DOs
def delete_do_instance():
    values = admin.login()
    csvfile = admin.opencsv()
    txtfile = admin.opentxt()
    for row in csvfile:
        archival_object_uri = row[0]
        digital_object_uri = row[1] #may or may not need this...could just loop through instances and check for DOs, then delete
        #OR could find a specific digital object instance I want to delete
        try:
            archival_object_json = requests.get(values[0] + archival_object_uri, headers=values[1]).json()
            instance_list = list(archival_object_json['instances'])
            if digital_object_uri == '':
                for instance in instance_list:
                    if instance['instance_type'] == 'digital_object':
                        archival_object_json['instances'].remove(instance)
                archival_object_data = json.dumps(archival_object_json)
                archival_object_update = requests.post(values[0] + archival_object_uri, headers=values[1], data=archival_object_data).json()
                admin.writetxt(txtfile, archival_object_update)
                print(archival_object_update)
            else:
                for instance in instance_list:
                    if 'digital_object' in instance:
                        if instance['digital_object'] == {'ref': digital_object_uri}:
                            archival_object_json['instances'].remove(instance)
                archival_object_data = json.dumps(archival_object_json)
                archival_object_update = requests.post(values[0] + archival_object_uri, headers=values[1], data=archival_object_data).json()
                admin.writetxt(txtfile, archival_object_update)
                print(archival_object_update)
        except:
            txtfile.write('error, could not update ' + str(archival_object_uri))
            continue

#this can work for any kind of AS object that has its own URI - i.e. agents, subjects, archobjs, resource, dos, classifications, etc.
def delete_records():
    values = admin.login()
    csvfile = admin.opencsv()
    txtfile = admin.opentxt()
    for row in csvfile:
        record_uri = row[0]
        try:
            record_json = requests.get(values[0] + record_uri, headers=values[1]).json()
            record_data = json.dumps(record_json)
            delete = requests.delete(values[0] + record_uri, headers=values[1], data=record_data).json()
            admin.writetxt(txtfile, delete)
            print(delete)
        except:
            txtfile.write('error, could not delete ' + str(record_uri))
            continue