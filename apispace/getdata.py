#/usr/bin/python3
#~/anaconda3/bin/python

import requests, json, csv, subprocess, os, re
from apispace import admin

global_record_types = ['agents/corporate_entities', 'agents/families', 'agents/people', 'agents/software', 'by-external-id', 'config/enumerations', 'container_profile',
                       'location_profiles', 'locations', 'permissions', 'reports', 'repositories', 'schemas', 'subjects', 'terms', 'users', 'users/complete'
                       'vocabularies']

repo_record_types = ['accessions', 'archival_objects', 'classification_terms', 'classifications', 'current_preferences', 'digital_object_components',
                     'digital_objects', 'events', 'groups', 'jobs', 'jobs/active', 'jobs/archived', 'jobs/import_types', 'preferences', 'rde_templates',
                     'resources', 'top_containers']

#Gets a list of enumerations
def get_enumerations():
    values = admin.login()
    output = admin.opentxt()
    enumerations = requests.get(values[0] + '/config/enumerations?all_ids=true', headers=values[1]).json()
    json.dump(enumerations, output, indent=4, separators=(',', ':'))
    output.close()

#Gets JSON for record types which are specific to a repository
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

#Gets JSON for record types shared across repositories
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

#Takes a single resource ID as input and outputs EAD
def export_ead(repo_id, resource):
    values = admin.login()
    output = admin.opentxt()
    get_ead = requests.get(values[0] + '/repositories/' + str(repo_id) + '/resource_descriptions/' + str(resource) + '.xml?include_unpublished=true', headers=values[1], stream=True).text
    output.write(str(get_ead))
    output.close()

'''Takes a list of resource URIs, gets its EAD, and transforms it to Yale's BPG guidelines. Also need to add validation

Note - URIs will have to be formatted like /repositories/12/resource_descriptions/resource_id.xml'''
def etv_ead():
    values = admin.login()
    inputfile = admin.readtxt()
    outputfile = admin.opentxt()
    dirpath = admin.setdirectory()
    print('Downloading EAD files to directory')
    for ead_uri in inputfile:
        get_ead = requests.get(values[0] + ead_uri + '.xml?include_unpublished=true', headers=values[1], stream=True).text
        #Finds URLs with 2-digit repo ids
        if re.search(r'[0-9]', ead_uri[15]):
            outfile = admin.openxml(dirpath, ead_uri[39:].rstrip())
            outfile.write(str(get_ead).rstrip())
        #Others - assumes it's a 1-digit repo id. How many institutions will have more than 99 repositories?
        else:
            outfile = admin.openxml(dirpath, ead_uri[38:].rstrip())
            outfile.write(str(get_ead).rstrip())
    '''the subprocess call cannot take the EAD from AS directly as input. First need to save the file, and then run the 
    transformation over each file'''
    print('Done!')
    print('Transforming EAD files to Yale Best Practices guidelines')
    filelist = os.listdir(dirpath)
    os.makedirs(dirpath + '/outfiles')
    for file in filelist:
        #finds all the EAD files in the working directory
        if file[-3:] == 'xml':
            #haven't changed the hard coding of the command or the xsl file yet
            subprocess.run(["java", "-cp", "/usr/local/Cellar/saxon/9.8.0.4/libexec/saxon9he.jar", "net.sf.saxon.Transform", 
                            "-s:" + dirpath + '/' + file, 
                            "-xsl:" + dirpath + "/transformations/yale.aspace_v112_to_yalebpgs.xsl", 
                            "-o:" + dirpath + '/outfiles/' + file[:-4] + "_out.xml"])
    '''next we need to validate each output file against the EAD 2002 schema and the local Yale schematron'''
    print('Done!')
    print('Validating transformations against EAD 2002 and Schematron schemas')
    newfilelist = os.listdir(dirpath + '/outfiles')
    for outfile in newfilelist:
        subprocess.Popen(["/Users/aliciadetelich/git/crux/target/crux-1.3-SNAPSHOT-all.jar", "-s", 
                        dirpath + "/transformations/yale.aspace.ead2002.sch",
                        dirpath + '/outfiles/' + outfile], stdout=outputfile, stderr=subprocess.PIPE, 
                             encoding='utf-8')
        subprocess.Popen(["/Users/aliciadetelich/git/crux/target/crux-1.3-SNAPSHOT-all.jar", 
                              dirpath + '/outfiles/' + outfile], stdout=outputfile, stderr=subprocess.PIPE, 
                             encoding='utf-8')
    print('All Done! Check outfile for validation report')


#Takes a list of resource IDs as input and outputs EAD
#add subprocess option here for running transformations
#Can do an ead3 option too
def export_eads(repo_id):
    values = admin.login()
    infile = admin.readtxt()
    dirpath = admin.setdirectory()
    for resource in infile:
        get_ead = requests.get(values[0] + '/repositories/' + str(repo_id) + '/resource_descriptions/' + str(resource) + '.xml?include_unpublished=true', headers=values[1], stream=True).text
        outfile = admin.openxml(dirpath, resource)
        outfile.write(str(get_ead))
        outfile.close()
    input.close()
        
def export_all_ead(repo_id):
    values = admin.login()
    dirpath = admin.setdirectory()
    get_ids = requests.get(values[0] + '/repositories/' + str(repo_id) + '/resources?all_ids=true', headers=values[1]).json()
    for resource in get_ids:
        get_ead = requests.get(values[0] + '/repositories/' + str(repo_id) + '/resource_descriptions/' + str(resource) + '.xml?include_unpublished=true', headers=values[1], stream=True).text
        outfile = admin.openxml(dirpath, resource)
        outfile.write(str(get_ead))
        outfile.close()

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

#possibly a place to wrap some sql queries

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

