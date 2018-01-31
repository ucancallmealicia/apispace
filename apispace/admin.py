#/usr/bin/python3
#~/anaconda3/bin/python

import requests
import csv
import pymysql
import json
from apispace import config

################## LOGIN FUNCTIONS ####################

def login():
    #if all values are present in config file...
    if config.username and config.api_url and config.password != '':
        auth = requests.post(config.api_url+'/users/'+config.username+'/login?password='+config.password).json()
        if 'session' in auth:
            session = auth["session"]
            headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}
            print('Login successful! Connected to ' + str(config.nickname))
            return (config.api_url, headers)
        else:
            print('Login failed! Check credentials and try again')
            return  
    #if one or more values is missing from config file...
    else:
        print('One or more login credentials missing from config.py file!')
        api_url = input('Please enter the ArchivesSpace API URL: ')
        username = input('Please enter your username: ')
        password = input('Please enter your password: ')
        auth = requests.post(api_url+'/users/'+username+'/login?password='+password).json()
        #if session object is returned then login was successful; if not it failed.
        if 'session' in auth:
            session = auth["session"]
            headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}
            print('Login successful!')
            return (api_url, headers)
        else:
            print('Login failed! Check credentials and try again')
            return
            
def login_db():
    '''This function logs into the ArchivesSpace Database'''
    #If all credentials are present in config file...
    if config.db_host and config.db_name and config.db_port and config.db_pw and config.db_un != '':
        print('Connecting you to the database...')
        connection = pymysql.connect(host=config.db_host,
                                 port = int(config.db_port),
                                 user=config.db_un,
                                 password=config.db_pw,
                                 db=config.db_name)
        print('Connected!')
        curse = connection.cursor()
        return curse
    else:
        print('One or more login credentials missing from config.py file!')
        db_name = input('Please enter the database name: ')
        db_host = input('Please enter the database host name: ')
        db_port = input('Please enter the database port: ')
        db_un = input('Please enter the database username: ')
        db_pw = input('Please enter the database password: ')
        print('Connecting you to the database...')
        connection = pymysql.connect(host=db_host,
                                 port = int(db_port),
                                 user=db_un,
                                 password=db_pw,
                                 db=db_name)
        print('Connected!')
        curse = connection.cursor()
        return curse

################## INPUT/OUTPUT FILE FUNCTIONS ####################

def opencsv():
    '''This function opens a csv file'''
    input_csv = input('Please enter path to CSV: ')
    file = open(input_csv, 'r', encoding='utf-8')
    csvin = csv.reader(file)
    next(csvin, None)
    return csvin

def opencsvdict():
    '''This function opens a csv file in DictReader mode'''
    input_csv = input('Please enter path to CSV: ')
    file = open(input_csv, 'r', encoding='utf-8')
    csvin = csv.DictReader(file)
    return csvin

def opencsvout():
    output_csv = input('Please enter path to output CSV: ')
    file = open(output_csv, 'a', encoding='utf-8', newline='')
    csvout = csv.writer(file)
    return csvout

def readtxt():
    filepath = input('Please enter path to input text file: ')
    filename = open(filepath, encoding='utf-8')
    read = filename.read()
    return read

def opentxt():
    filepath = input('Please enter path to output text file: ')
    filename = open(filepath, 'a', encoding='utf-8')
    return filename

def setdirectory():
    directory = input('Please enter path to output directory: ')
    return directory

def opentxts(directory, filename):
    filepath = open(directory + '/' + filename, 'w', encoding='utf-8')
    return filepath

def writealltxt(file, jsonname):
    for key, value in jsonname.items():
        file.write('%s:%s\n' % (key, value) + '\n')

def writetxt(file, jsonname):
    for key, value in jsonname.items():
        if key == 'status':
            file.write('%s:%s\n' % (key, value))
        if key == 'uri':
            file.write('%s:%s\n' % (key, value) + '\n')
        if key == 'id':
            file.write('%s:%s\n' % (key, value) + '\n')
        if key == 'error':
            file.write('%s:%s\n' % (key, value) + '\n')

################## ARCHIVESSPACE ADMIN-TYPE/GLOBAL FUNCTIONS ####################

def setdefaultvalues():
    print('placeholder')
    
def update_enum_val_positions():
    values = login()
    csvfile = opencsv()
    for row in csvfile:
        enum_val_uri = row[0]
        desired_position = row[1]
        enum_vals = requests.get(values[0] + enum_val_uri, headers=values[1]).json()
        enum_val_json = requests.post(values[0] + enum_val_uri + '/position?position=' + desired_position, headers=values[1], data=json.dumps(enum_vals)).json()
        print(enum_val_json)

def extent_calculator():
    values = login()
    csvfile = opencsv()
    csvoutfile = opencsvout()
    headers = ['uri', 'title', 'total_extent', 'container_count']
    csvoutfile.writerow(headers)
    x = 0
    for row in csvfile:
        x = x + 1
        data = []
        uri = row[0]
        extent_calculator = requests.get(values[0] + '/extent_calculator?record_uri=' + uri, headers=values[1]).json()
        for key, value in extent_calculator.items():
            if key == 'object':
                for subkey, subvalue in value.items():
                    if subkey == 'uri':
                        data.insert(0, subvalue)
                    if subkey == 'title':
                        data.insert(1, subvalue)
            if key == 'total_extent':
                data.insert(2, value)
            if key == 'container_count':
                data.insert(3, value)
        csvoutfile.writerow(data)
        print('Writing record number ' + str(x) + ' to file.')
    print('All done! Check outfile for details.')                    

def get_tree(repo, record_id):
    values = login()
    output = opentxt()
    resource = requests.get(values[0] + '/repositories/' + str(repo) + '/resources/' + str(record_id) + '/tree', headers=values[1]).json()
    json.dump(resource, output, indent=4, separators=(',', ':'))
    output.close()

def get_tree_nodes():
    values = login()
    csvfile = opencsv()
#    csvout = opencsvout()
    output = opentxt()
    for row in csvfile:
        ao_uri = row[0]
        resource_uri = row[1]
        tree_node = requests.get(values[0] + resource_uri + '/tree/node?node_uri=' + ao_uri, headers=values[1]).json()
#        row.append([tree_node])
#        csvout.writerow(row)
        json.dump(tree_node, output, indent=4, separators=(',', ':'))
    output.close()

#add functions for time keeping
#use this to post an edited JSON file
#def post_json

#insert other AS administrative-type stuff here - deleted values subpackage
#is deleting enumeration values possible only by fucking with the YML file, or can you do it some other way?

#should I make publish and unpublish an admin function since it stretches across everything.
    