#/usr/bin/python3
#~/anaconda3/bin/python

import pprint, requests, re
from collections import defaultdict
from apispace import admin
from apispace.admin import writealltxt
#from easydict import EasyDict as edict

''' Pulls in the ArchivesSpace schema from the API '''
def get_new_schemas():
    values = admin.login()
    get_schemas = requests.get(values[0] + '/schemas', headers=values[1]).json()
    return(get_schemas)

''' Pulls in a particular ArchivesSpace schema from the API '''
def get_new_schema(schema):
    values = admin.login()
    get_schema = requests.get(values[0] + '/schemas/' + str(schema), headers=values[1]).json()
    return(get_schema)

''' This function links up notes with the top-level records to which they apply'''
#Can I add this to the schema_to_dict so I only have to call schema once?
def parse_notes():
    #loads in the schema
    s = get_new_schemas()
    #sets up a defaultdict 
    new_dict = defaultdict(list)
    #loops through each JSONModel schema dictionary
    for key, value in s.items():
        for k, v in value.items():
            #gets all the properties
            if k == 'properties':
                #loops through the value of the properties key, which is also a dict
                for kk, vv in v.items():
                    if kk == 'subnotes':
                        y = vv['items']['type']      
                        for item in y:
                            for v3 in item.values():
                                #gets rid of JSONModel: object stuff
                                v3 = v3[11:-8]
                                new_dict[key].append(v3)
                    #finds notes
                    if re.search(r'^notes', kk):
                        #finds the note type
                        x = vv['items']['type']
                        if type(x) is str:
                            x = x[11:-8]
                            new_dict[key].append(x)
                        else:
                            for member in x:
                                s = member['type'][11:-8]
                                #this creates the dict for each top_level record type which contains a list of the notes
                                #which are applicable to each
                                new_dict[key].append(s)
                    #finds names
                    if re.search('^names', kk):
                        #finds the name type
                        x = vv['items']['type']    
                        if type(x) is str:
                            x = x[11:-8]
                            new_dict[key].append(x)
                        else:
                            for member in x:
                                s = member['type'][11:-8]
                                new_dict[key].append(s)
    #turns the default dict into an actual dict, with the top-level record type as the key and 
    #lists of the note and name types which apply to those top-level records as the values.
    new_dict = dict(new_dict)
    #this goes ahead and turns the list into a dict using the list members as keys.
    for key4, value4 in new_dict.items():
        value4 = dict.fromkeys(value4)
        new_dict[key4] = value4
    #pprint.pprint(new_dict)
    return(new_dict)  
    
#parse JSON schema for use in record creation functions - everything but notes and names.
def schema_to_dict():
    #load in the schema
    schema = get_new_schemas()
    #create dictionary to store data types and values
    schema_dict = {}
    ref_list = []
    weird_list = ['linked_agents', 'linked_events']
    #loop through top level of schema and retrieve top-level record name
    for key, value in schema.items():
        #loop through the dictionaries which are the values of the top-level keys
        for subkey, subval in value.items():
            #find the properties key, which holds all of the fields
            if subkey == 'properties':
                #store the values in a list
                prop_list = list(subval.keys())
                #create a dictionary with the top-level record as the key and a list of its fields as the value, then change
                #that list to a dictionary with the fields as keys and a value of none. This way can add subrecords and stuff
                #later.
                schema_dict[key] = dict.fromkeys(prop_list)
                #feels weird to have this all here, but I think it should be since this is where I called the schema- I could do it
                #again but that seems excessive
                for k, v in subval.items():
                    #print('property: ' + str(k))
                    #print('values: ' + str(v))
                    for kkk, vvv in v.items():
                        if type(vvv) is dict:
                            if 'properties' in vvv.keys():
                                if k not in ref_list:
                                    if k not in weird_list:
                                        ref_list.append(k)
                            elif 'ref' in vvv.keys():
                                if k not in ref_list:
                                    if k not in weird_list:
                                        ref_list.append(k)
                        if k in weird_list:
                            if kkk == 'items':
                                for kkkk, vvvv in vvv.items():
                                    if kkkk == 'properties':
                                        new_dict = dict.fromkeys(vvvv.keys())
                                        schema_dict[key][k] = new_dict
                                        #may need this to add enums
                                        for k5, v5 in vvvv.items():
                                            #print(k5)
                                            #print(v5)
                                            for k6 in v5.keys():
                                                if k6 == 'dynamic_enum':
                                                    #print(v5.get(k6))
                                                    schema_dict[key][k][k5] = v5.get(k6)
                    #could do a from keys if I want to add the actual enumerations
                    for kk, vv in v.items():
                        if 'enum' in kk:
                            schema_dict[key][k] = vv
    #pprint.pprint(schema_dict)
    #print(ref_list)
    return(schema_dict, ref_list)

#This adds the first round of subrecord values to the top-level record type schema
#Works recursively
#the reason the ref list doesn't work is because this overrides it...
def parse_schema():
    #stores the schema dictionary in a variable
    schema_d = schema_to_dict()
    #pulls in the result of the note stuff and stores in a variable
    notes_parsed = parse_notes()
    weird_list = ['location', 'enumeration']
    #create an empty dictionary to store parsed schema
    valuedict = {}
    #loops through the top level of the schema dictionary and adds the keys and values to the empty dictionary
    for key, val in schema_d[0].items():
        valuedict[key] = val
    #loops through each key (JSONModel schema) and each value list (the list of properties for the key)
    for k, value_d in schema_d[0].items():
        #loops through each property in the valuelist looking for subrecords
        for k2 in value_d.keys():
            if k2 in schema_d[0].keys():
                if k2 not in weird_list:
                    valuedict[k][k2] = schema_d[0].get(k2)
#           deals with silly plural nonsense - dates, extents, etc.
            elif k2[:-1] in schema_d[0].keys():
#                newdict = dict.fromkeys(schema_d.get(member[:-1]))
                valuedict[k][k2] = schema_d[0].get(k2[:-1])
        #this deals with names and notes - could put in a different function?
        #loops through top level records with notes (k3), and the dictionaries which contain the
        #note types (v3)
        for k3, v3 in notes_parsed.items():
            note_dict = {}
            name_dict = {}
            subnote_dict = {}
            #limits the schema to only the top-level records with notes or names
            if k3 == k:
                if 'note' in k3:
                    for k8 in v3.keys():
                        subnote_dict[k8] = schema_d[0].get(k8)
                    valuedict[k3]['subnotes'] = subnote_dict
                else:
                    #the value of the note dictionaries is a dictionary of note types; this loops throught the keys
                    for k4 in v3.keys():
                        #if the note or name type is in the schema
                        if k4 in schema_d[0].keys():
                            #print(schema_d.get(k4))
                            #this is the note or name type. 
                            if 'note' in k4:
                                note_dict[k4] = schema_d[0].get(k4)
                                #why did I take this out? Do I need it for the names?
                                #note_dict.update(schema_d.get(k4))
                            elif 'name' in k4:
                                name_dict[k4] = schema_d[0].get(k4)
                                name_dict.update(schema_d[0].get(k4))       
                    if name_dict != {}:
                        valuedict[k]['names'] = name_dict
                    if note_dict != {}:
                        valuedict[k]['notes'] = note_dict
    #for k9, v9 in valuedict.items()
    for value in valuedict.values():
        for k5, v5 in value.items():
            if k5 in schema_d[1]:
                value[k5] = {'ref': None}
            if type(v5) is dict:
                for k6 in v5.keys():
                    if k6 in schema_d[1]:
                        v5[k6] = {'ref': None}
    #pprint.pprint(valuedict)
    return(valuedict)

#Have to loop through the enumeration values within the enumerations - they are all there though...
def get_enums():
    values = admin.login()
    #scheme = parse_schema()
    enumerations = requests.get(values[0] + '/config/enumerations?all_ids=true', headers=values[1]).json()
    for enumeration in enumerations:
        #want to match the schema keys (and subkeys) with the names
        pprint.pprint(enumeration['name'])
        #if there is a match want to append the whole valuelist as a value of the schema key/subkeys
        pprint.pprint(enumeration['values'])

#add_refs()
#parse_notes()
#schema_to_dict()
parse_schema()
#get_enums()

'''
To-Do, Thoughts, Etc.

-Location for external docs is dif than location for top containers, yet they have the same name - both should be refs, though?
    -Can probably differentiate somehow?
    
- "job" (and term, etc.) issues, - job has a key which is entitled job, and so inherits all of the other top-level job stuff;
 fixed some of the recursion issues but not all - figure all this out.

-add JSONModel types to values - pull from key

-Could theoretically look up the actual enums too, now that I have their names- but this would be a different API request.
    - Do this - find anything that does not have the value of none, and look up enums?

-Check if other things are missing from schema
-Documentation/comments
-Remove extra call to schema?

DONE:
--Add {'ref': None} to records where appropriate - replace hard-coded list - DONE
    -Get ref list from schema - find anything with a ref - not sure what the format looks like
-Subnote info for note_multipart and note_bioghist - DONE
-Get enums for linked agents and events - DONE
-Get linked agents and events - DONE
-Add enums if possible - DONE (but not for linked agents and events)
-Test pulling in schema from API and manipulating using functions - DONE
-Notes which are attached to the rights statements - DONE

-Obviously most of these functions are pretty hacky and need to be cleaned up, but this serves as a proof of concept/starting point
 '''

