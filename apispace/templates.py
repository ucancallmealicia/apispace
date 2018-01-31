#/usr/bin/python3
#~/anaconda3/bin/python

import csv

#should use same names as JSON, except for URIs; so can eventually use DictReader for all columns
#solution to index error problem- make sure that all spreadsheets have all columns even if they aren't all filled out
#that was can just skip end date, etc. if blank

def config_file():
    config_dict = "{\"api_url\": \"test\", \"username\": \"test\",\"password\": \"test\",\"nickname\": \"test\",\"db_name\": \"test\",\"db_host\": \"test\",\"db_port\": \"test\",\"db_un\": \"test\",\"db_pw\": \"test\"}"
    return(config_dict)

def write_config():
    config_json = config_file()
    directory = input('Please enter path to output folder: ')
    file = open(directory + '/config_file.json', 'w', encoding='utf-8', newline='')
    file.write(str(config_json))
    print('All Done!')

#Templates for record creation. Could also be used for updating records. How to indicate which are required?
def templates():
    #make sure values match JSON values
    all_templates = {'repository': ['repo_name', 'repo_code'],
                 'accession': ['repo_uri', 'title', 'identifier', 'accession_date', 'inventory', 'disposition', 'display_string',
                               'general_note', 'provenance', 'publish', 'acquisition_type', 'access_restrictions'],
                 'resource': ['repo_uri', 'id_0', 'title', 'language', 'level', 'begin', 'end', 'date_type',
                              'date_label', 'extent_type', 'extent_portion', 'extent_number', 'container_summary'],
                 'archival_object': ['resource_uri', 'repo_uri', 'title', 'level', 'parent_series_uri', 'component_id'],
                 'digital_object': ['repo_uri', 'digital_object_id', 'title'],
                 'digital_object_component': ['repo_uri', 'parent_uri', 'component_id', 'title'],
                 'date': ['record_uri', 'begin', 'end', 'expression', 'date_type', 'label'],
                 'extent': ['record_uri', 'container_summary', 'extent_type', 'number', 'portion', 'dimensions', 'physical_details'],
                 'external_document': ['record_uri'],
                 'external_id': ['record_uri'],
                 'file_version': ['record_uri', 'file_uri', 'identifier'],
                 'instance': ['record_uri'],
                 'top_container': ['record_uri'],
                 'sub_container': ['top_container_uri'],
                 'container_profile': [],
                 'location': [],
                 'location_profile': [], 
                 'event': [],
                 'classification': [],
                 'classification_term': [],
                 'agent': [],
                 'subject': [],
                 'note_singlepart': ['record_uri', 'note_text', 'note_type'],
                 'note_multipart': ['record_uri', 'note_text', 'note_type'],
                 'rights_restrictions': ['record_uri', 'persistent_id', 'begin', 'end', 'local_type', 'note_type']
        }
    return all_templates

#Should I add something here to automatically open the containing folder? Or have it make a folder?

def download_templates():
    templated = templates()
    directory = input('Please enter path to output folder: ')
    for key, value in templated.items():
        file = open(directory + '/' + str(key) + '.csv', 'w', encoding='utf-8', newline='')
        csvout = csv.writer(file)
        csvout.writerow(value)

def download_template(template):
    templated = templates()
    for key, value in templated.items():
        if key == template:
            directory = input('Please enter path to output folder: ')
            file = open(directory + '/' + str(key) + '.csv', 'w', encoding='utf-8', newline='')
            csvout = csv.writer(file)
            csvout.writerow(value)