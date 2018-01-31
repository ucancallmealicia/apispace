#/usr/bin/python3
#~/anaconda3/bin/python

import json

''' To-Do:
Create a function which will load a configuration file from the user. Include template in templates module

'''


#Surely this is incorrect
def api_settings(url, un, pw, nick):
    global api_url
    api_url = url
    global username
    username = un
    global password
    password = pw
    global nickname
    nickname = nick

def db_settings(name, host, port, un, pw):
    global db_name
    db_name = name
    global db_host
    db_host = host
    global db_port
    db_port = port
    global db_un
    db_un = un
    global db_pw
    db_pw = pw

def clear_settings(thing):
    if thing == 'api':
        global api_url
        api_url = ''
        global username
        username = ''
        global password
        password = ''
        global nickname
        nickname = ''
    if thing == 'db':
        global db_name
        db_name = ''
        global db_host
        db_host = ''
        global db_port
        db_port = ''
        global db_un
        db_un = ''
        global db_pw
        db_pw = ''

def loadconfig():
    file = input('Please enter path to configuration file: ')
    try:
        openconfig = open(file)
        config_json = json.load(openconfig)
        print(config_json)
        print('Thank you, your file has been loaded.')
        global api_url
        api_url = config_json['api_url']
        global password
        password = config_json['password']
        global username
        username = config_json['username']
        global nickname
        nickname = config_json['nickname']
    except:
        print('Sorry, your file could not be loaded.')
    
 
api_url = ''
username = ''
password = ''
nickname = ''

db_name = ''
db_host = ''
db_port = ''
db_un = ''
db_pw = ''

