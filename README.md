# apispace

A beta/hyper-prototypical/incomplete/work-in-progress Python package that uses CSVs to interact with the ArchivesSpace API.

NOTE: Use at your own risk. Much of this is still unfinished, but the description functions have been tested. Further
additions to the code and more documentation is coming soon.

### Requirements  
- Python 3.4+
- `requests` module
- `pymysql` module
- Access to ArchivesSpace API
- Access to ArchivesSpace Database

### Installation

In Terminal, clone repository and cd to top-level apispace directory, then enter

`pip install apispace`

### Set or load `config` file

To enter login settings into the console:

	>>> import apispace
	>>> config.api_settings(url, username, password, nickname)
	>>> print(api_url)
	url
	>>> config.db_settings(name, host, port, un, pw)
	>>> print(db_name)
	name
	
To download a configuration JSON file template:

	>>> import apispace
	>>> templates.write_config()
	Please enter path to output folder: 
	>>> All Done!

To load a configuration JSON file:

	>>> import apispace
	>>> config.loadconfig()
	Please enter the path to your config file: /Users/user/Desktop/confix.json
	>>> Thank you, config file is loaded.

All functions will work without entering credentials, but users must enter credentials each time a function
is called.

To clear login settings, run:

	>>> config.clear_settings(api)
	>>> print(password)
	
	>>> config.clear_settings(db)
	>>> print(db_name)
	
	>>>

### Templates

A variety of CSV templates are available for use with `apispace` functions. To download all templates, do:

	>>> import apispace
	>>> templates.download_templates()
	>>> Please enter path to output folder: Users/username/Desktop/templates
	>>>

To download a single template, do:

	>>> import apispace
	>>> templates.download_template('accessions')
	>>> Please enter path to output folder: Users/username/Desktop/templates
	>>>

Users may find it beneficial to create a separate directory to store template files.

### Administrative Functions 

This submodule includes basic login and file handling functions. It also includes a few basic ArchivesSpace functions, including functions to retrieve and update
set default values and to update enumeration value positions.

admin.**login()**  

Log in to the ArchivesSpace API. Uses optional `config` file to retrieve login information. See instructions above to set up `config` file.

To log in and perform a test GET request, try the following:

	>>> import apispace
	>>> values = admin.login()
	Login successful! Connected to ArchivesSpace TEST
	>>> example = requests.get(values[0] + '/repositories, headers=values[1]).json()
	>>> print(example)
	[List of repositories]

If the config file is not set, a call to the login function will prompt the user for credentials.

admin.**login\_db()**  

Log in to the ArchivesSpace database. Uses optional `config` file to retrieve login information. See instructions above to set up `config` file.

If the config file is not set, a call to the login_db function will prompt the user for credentials.

admin.**opencsv()**  

Opens an input CSV file. This function is called in nearly every other function in this package.

admin.**opencsvdict()**

Opens an input CSV file in DictReader mode. This function is used in functions which allow for variable numbers of record updates.

admin.**opencsvout()**  

Open an output CSV file. This function is used in other functions to store output data.

admin.**opentxt()**  

Open an output text file. This function is used in other functions to store log data.

admin.**writetxt(f, j)**  

Write to an output text file. This function is used in other functions to store JSON data for individual records.

admin.**writealltxt(f, j)**  

Write to an output text file. This function is used in other functions to store JSON data for a batch of records.

admin.**setdefaultvalues()**  

admin.**update\_enum\_val\_positions()**  

Updates the position of enumeration values, using a CSV as input. To use the CSV output from `getdata.get_enumerations(enumeration)` as input
for this function, simply change the position values to whatever is desired.

To use, do the following:

	>>> import apispace
	>>> admin.update_enum_val_positions()
	Login Successful! Connected to ArchivesSpace TEST
	Please enter path to input CSV: /Users/username/Desktop/updated_enum_positions.csv
	<Enumeration_Value xxxxx>
	<Enumeration_Value xxxxx>
	>>> 

### Schema Module

This submodule takes the JSONModel schemas for ArchivesSpace and manipulates them into a format in which they can be easily
accessed by the description functions in this module. The goal is to abstract the description functions - especially
the record creation functions - as much as possible, and to pull in data directly from the schema. 

This portion of the module is not fully fleshed out yet, so other functions in the description submodule for
record creation are still available.

### Description Functions  

This submodule includes a variety of functions which create, update, and delete descriptive records and subrecords.

Use `template` functions to download CSV templates for use with `description` functions

#### Create Descriptive Records

description.**create_records(jsonmodel_type, **subrecords)**

Creates one or more records of any type, with any number of record and subrecord fields. This function pulls in data 
from the ArchivesSpace schema via a request to the API. Gien the record type and any subrecords as arguments, it 
matches the record type, the properties of each record type, and any subrecord fields with the data in the schema, 
and then constructs a JSON object based on the column headers of the input CSV.

This function enables users to create any kind of record, with any number of fields, using a single function. Because
the schema is pulled in from the API, users will be able to utilize the schema which corresponds to their version of
ArchivesSpace.

description.**repositories()**  

Creates one or more minimally-populated repository records using _repositories.csv_ as input.

To use, do the following:

Complete repositories.csv template, i.e.:

| repo\_name                   | repo\_code    |
| ---------------------------- | ------------- |
| Manuscripts and Archives     | mssa          |
| Arts Library                 | arts          |
| Medical Library              | med           |

Run repositories() function:

	>>> import apispace
	>>> description.repositories()
	Login Successful! Connected to ArchivesSpace TEST
	Please enter path to input CSV: /Users/username/Desktop/repositories.csv
	{Status: Updated...}
	{Status: Updated...}
	{Status: Updated...}

description.**accessions()**  
Creates one or more minimally-populated repository record using _accessions.csv_ as input.

description.**resources()**  
Creates one or more minimally-populated resource records using _resources.csv_ as input

description.**archival\_objects()**  
Creates one or more minimally-populated archival object records using _archival\_objects.csv_ as input

description.**digital\_objects()**  
Creates one or more minimally-populated digital object records using _digital\_objects.csv_ as input

description.**dig\_object\_components()**  
Creates one or more minimally-populated digital object records using _dig\_obj\_components.csv_ as input

description.**dates()**  
Creates dates to be added to existing descriptive records, using _dates.csv_ as input

description.**extents()**  
Creates extents to be added to existing descriptive records, using _extents.csv_ as input

description.**external\_docs()**  
Creates external documents to be added to existing descriptive records, using _external\_docs.csv_ as input

description.**external\_ids()**  
Creates external IDs to be added to existing descriptive records, using _external\_ids.csv_ as input

description.**file\_versions()**  
Creates file versions to be added to existing descriptive records, using _file\_versions.csv_ as input

description.**revision\_statements()**  
Creates finding aid revision statements to be added to existing descriptive records, using _revision\_statements.csv_ as input

description.**singlepart\_notes()**  
Creates singlepart notes to be added to existing descriptive records, using a CSV as input

description.**multipart\_notes()**  
Creates multipart notes to be added to existing descriptive records, using a CSV as input

description.**rights\_restrictions()**  
Creates rights restrictions to be added to existing conditions governing access or conditions governing use notes, using a CSV as input

description.**note\_bioghist()**  
Creates a biographical history note to be added to an existing descriptive record, using a CSV as input

description.**note\_abstract()**  
Creates an abstract note to be added to an existing descriptive record, using a CSV as input

description.**note\_bibliography()**  
Creates a bibliography to be added to an existing descriptive record, using a CSV as input

#### Update Descriptive Records

description.**update\_record\_component()**  
Updates any single top-level (string) record component, using a CSV as input

description.**update\_record\_components(\*\*args)**  
Updates one or more top-level record components, using a CSV as input

description.**update\_record\_pub\_status()**  
Updates the publication status of one or more descriptive records, using a CSV as input

description.**update\_subrecord\_component()**  
Updates any single sub-record (module) component, using a CSV as input

description.**update\_subrecord\_components(\*\*args)**  
Updates one or more sub-record (module) components, using a CSV as input

description.**update\_note\_component()**  
Update any single note component, using a CSV as input

description.**update\_note\_components(\*\*args)** - **_NOT YET WRITTEN_**  
Update one or more note components, using a CSV as input

description.**update\_note\_pub\_status()**  
Update the publication status of one or more notes, using a CSV as input

description.**replace\_note\_by\_id()**  
Replace the text of an existing note using its persistent ID

#### Delete Descriptive Records

description.**delete\_notes()**  
Delete one or more notes

description.**delete\_subrecords()**  
Delete one or more subrecords (modules) from a descriptive record

description.**delete\_subrecord\_components()**  
Delete a given number of components from a subrecord

description.**delete\_do\_instance()**  
Delete a digital object instance. NOTE: Always delete a digital object instance before deleting the digital object itself.

description.**delete\_records()**  
Delete one or more descriptive records.

### Classification Functions  

classification.**create\_top\_level()**

classification.**create\_sub\_level()**  

classification.**create\_sub\_sub\_level()**  

classification.**link\_records()**  

classification.**get\_class\_uris()**  

classification.**get\_class\_rec\_links()** 

### Authority Functions

#### Agents

agent.**create\_agent()**  
Create one or more agent records using a CSV as input

agent.**update\_agent\_component()** - **_NOT YET WRITTEN_**

agent.**update\_agent\_components()** - **_NOT YET WRITTEN_**  

agent.**link\_agent()**  
Link one or more agent records to existing descriptive records, using a CSV as input

agent.**merge\_agents()** = **_NOT YET WRITTEN_**

#### Subjects

subject.**create\_subject()**  
Create one or more subjects using a CSV as input

subject.**update\_subject\_component()**  

subject.**update\_subject\_components()**  

subject.**link\_subject()** - **_NOT YET WRITTEN_**

subject.**delete\_subject()** - **_NOT YET WRITTEN_**  

### Physical Control Functions   

#### Containers

container.**create\_top\_container()**  
Creates one or more top containers using a CSV as input

container.**update\_tc\_components()**  

container.**create\_instances()**  
Links top containers to descriptive records, using a CSV as input

container.**create\_do\_instances()**  

container.**update\_sc\_components()**  
Updates subcontainer types and indicators, using a CSV as input. Ideal for making batch updates/corrections to folder numbers

container.**create\_container\_profiles()**  
Creates container profiles using a CSV as input

#### Locations

location.**create\_location()**  
Creates one or more locations using a CSV as input

location.**update\_location(\*\*args)**  
Updates a given number of location components using a CSV as imput

event.**create\_event()**  


### Reference Functions

schema.**schema()**  
Prints the ArchivesSpace schema

`datatypes` submodule  

### Retrieving Data

getdata.**get_enumerations()**  

Database query to return the uri, name, and position of all enumeration values in a given enumeration.

getdata.**get\_repo\_json()**

getdata.**get\_global\_json()**

getdata.**get\_repo\_ids()**  

getdata.**get\_global\_ids()**  

getdata.**get\_note\_ids()**  

getdata.**get\_uris()**  

getdata.**extent_calculator()**  - **_NEED TO MOVE_**

Retrieves calculated extent values for a list of resources, using a CSV of ArchivesSpace URIs as input

getdata.**get_tree(repo, resource)** - **_NEED TO MOVE_**

Retrieves the record tree for a resource