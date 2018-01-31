'''
Created on Jan 30, 2018

@author: aliciadetelich
'''
import requests
import json
from apispace import admin

#Includes assessment
#Includes collection management

def create_top_containers():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        barcode = row[0]
        indicator = row[1]
        container_profile_uri = row[2]
        locations = row[3]
        start_date = row[4]
        repo_num = row[5]
        if barcode != '':
            create_tc = {'barcode': barcode, 'container_profile': {'ref': container_profile_uri}, 'indicator': indicator,
                         'container_locations': [{'jsonmodel_type': 'container_location', 'status': 'current', 'start_date': start_date,
                                                  'ref': locations}],
                         'jsonmodel_type': 'top_container', 'repository': {'ref': repo_num}}
        else:
            create_tc = {'container_profile': {'ref': container_profile_uri}, 'indicator': indicator,
                         'container_locations': [{'jsonmodel_type': 'container_location', 'status': 'current', 'start_date': start_date,
                                                  'ref': locations}],
                         'jsonmodel_type': 'top_container', 'repository': {'ref': repo_num}}
        tcdata = json.dumps(create_tc)
        tcupdate = requests.post(values[0] + repo_num + '/top_containers', headers=values[1], data=tcdata).json()
        print(tcupdate)

#this has a display_string now too        
def update_tc_component():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        top_container_uri = row[0]
        component_to_update = row[1]
        update_text = row[2]
        tc_json = requests.get(values[0] + top_container_uri, headers=values[1]).json()
        tc_json[component_to_update] = update_text
        tc_data = json.dumps(tc_json)
        tc_update = requests.post(values[0] + top_container_uri, headers=values[1], data=tc_data).json()
        print(tc_update)
    
def update_tc_components():
    values = admin.login()
    csvfile = admin.opencsvdict()
    for row in csvfile:
        record_uri = row['uri']
        record_json = requests.get(values[0] + record_uri, headers=values[1]).json()
        for key, value in row.items():
            #so you can add a container location. There is another ref key in the collection key/val,
            #but you shouldn't need to add that, it will automatically show up when ao instance
            #is created
            if key == 'ref':
                for member in record_json['container_locations']:
                    member['ref'] = value
            #all other top container values can be modified this way
            else:
                record_json[key] = value
        record_data = json.dumps(record_json)
        record_update = requests.post(values[0] + record_uri, headers=values[1], data=record_data).json()
        print(record_update)

#add for digital object instance 
def create_instances():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        archival_object_uri = row[0]
        top_container_uri = row[1]
        child_type = row[2]
        child_indicator = row[3]
        grandchild_type = row[4]
        grandchild_indicator = row[5]
        instance_type = row[6]
        archival_object_json = requests.get(values[0] + archival_object_uri, headers=values[1]).json()
        if grandchild_type != '':
            new_instance = { "instance_type": instance_type, "jsonmodel_type": "instance", "sub_container": {"jsonmodel_type": "sub_container",
                                                                                                             "indicator_2": child_indicator,
                                                                                                             "type_2": child_type,
                                                                                                             "indicator_3": grandchild_indicator,
                                                                                                             "type_3": grandchild_type,
                                                                                                             "top_container": {"ref": top_container_uri}}}
        elif child_type != '':
            new_instance = { "instance_type": instance_type, "jsonmodel_type": "instance", "sub_container": {"jsonmodel_type": "sub_container",
                                                                                                             "indicator_2": child_indicator,
                                                                                                             "type_2": child_type,
                                                                                                             "top_container": {"ref": top_container_uri}}}
        else:
            new_instance = { "instance_type": instance_type, "jsonmodel_type": "instance", "sub_container": {"jsonmodel_type": "sub_container",
                                                                                                             "top_container": {"ref": top_container_uri}}}
        archival_object_json["instances"].append(new_instance)
        archival_object_data = json.dumps(archival_object_json)
        archival_object_update = requests.post(values[0]+archival_object_uri, headers=values[1], data=archival_object_data).json()
        print(archival_object_update)

def create_do_instances():
    return

#Updates sub_container components within an instance record - i.e child and grandchild types and indicators, and the top
#container URI. Don't have anything to update the instance type, but only because that's probably not necessary
#If there is more than one instance attached to the record to be updated, the position (0-n) must be specified in the CSV.
#Working on a better way to deal with this issue for all record types that can have multiple values
def update_sc_components(*field):
    values = admin.login()
    csvfile = admin.opencsvdict()
    fields = field
    for row in csvfile:
        record_uri = row[fields[0]]
        fieldlist = fields[1:]
        print(fieldlist)
        print(record_uri)
        if 'position' in fieldlist:
            record_json = requests.get(values[0] + record_uri, headers=values[1]).json()
            for field in fieldlist:
                for key, value in row.items():
                    if field == key:
                        print(value)
                        position = int(row['position'])
                        record_json['instances'][position]['sub_container'][key] = value
        else:
            record_json = requests.get(values[0] + record_uri, headers=values[1]).json()
            for field in fieldlist:
                for key, value in row.items():
                    if field == key:
                        print(value)
                        record_json['instances'][0]['sub_container'][key] = value
        record_data = json.dumps(record_json)
        record_update = requests.post(values[0] + record_uri, headers=values[1], data=record_data).json()
        print(record_update)
 
def create_container_profiles():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        name = row[0]
        extent_dimension = row[1]
        height = row[2]
        width = row[3]
        depth = row[4]
        dimension_units = row[5]
        #takes data from spreadsheet and builds JSON
        new_container_profile = {'jsonmodel_type': 'container_profile', 'name': name,
                                 'extent_dimension': extent_dimension, 'height': height,
                                 'width': width, 'depth': depth, 'dimension_units': dimension_units}
        container_profile_data = json.dumps(new_container_profile)
        #Posts JSON to ArchivesSpace
        create_profile = requests.post(values[0] + '/container_profiles', headers=values[1], data=container_profile_data).json()
        #Prints what is happening to IDLE window - will add an error log as well
        print(create_profile)

def create_locations():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        building = row[0]
        room = row[1]
        coordinate_1_label = row[2]
        coordinate_1_indicator = row[3]
        coordinate_2_label = row[4]
        coordinate_2_indicator = row[5]
        coordinate_3_label = row[6]
        coordinate_3_indicator = row[7]
        location_profile = row[8]
        if location_profile != '':
            new_location = {'jsonmodel_type': 'location', 'building': building,
                                     'room': room, 'coordinate_1_label': coordinate_1_label,
                                     'coordinate_1_indicator': coordinate_1_indicator,
                                     'coordinate_2_label': coordinate_2_label,
                                     'coordinate_2_indicator': coordinate_2_indicator,
                                     'coordinate_3_label': coordinate_3_label,
                                     'coordinate_3_indicator': coordinate_3_indicator,
                                     'location_profile': {'ref': location_profile}}
        else:
            new_location = {'jsonmodel_type': 'location', 'building': building,
                                     'room': room, 'coordinate_1_label': coordinate_1_label,
                                     'coordinate_1_indicator': coordinate_1_indicator,
                                     'coordinate_2_label': coordinate_2_label,
                                     'coordinate_2_indicator': coordinate_2_indicator,
                                     'coordinate_3_label': coordinate_3_label,
                                     'coordinate_3_indicator': coordinate_3_indicator}
        location_data = json.dumps(new_location)
        create_location = requests.post(values[0] + '/locations', headers=values[1], data=location_data).json()
        print(create_location)

#again, should i make it possible to just update the coordinates, not the whole location?
#also, this is basically the same as create, but with URI added. I think it could be combined;
#maybe add the uri to the last row and if it is empty then do the update, if not create a new one
def update_locations():
    return

#Add variable input functions...

def create_location_profiles():
    values = admin.login()
    csvfile = admin.opencsv()
    for row in csvfile:
        name = row[0]
        dimension_units = row[1]
        depth = row[2]
        width = row[3]
        height = row[4]
        new_location_profile = {'jsonmodel_type': 'location_profile', 'name': name,
                                 'height': height, 'width': width, 'depth': depth,
                                'dimension_units': dimension_units}
        location_profile_data = json.dumps(new_location_profile)
        create_profile = requests.post(values[0] + '/location_profiles', headers=values[1], data=location_profile_data).json()
        print(create_profile)


def create_event():
    return

def update_event():
    return

def link_event():
    return
    
def delete_event():
    return

def get_event():
    return
    
