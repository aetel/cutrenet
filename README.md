# cutrenet
This is a simple Python CRUD application to manage AETEL members.

# STILL IN DEVELOPMENT

## Use:
Launch setup.py, if a database exists it will use that, if not it will create one.
When database is fresh it creates a user admin@example.com/admin.
Then launch the main python script.
Go to /register to register a new member.

## To-Do:
* ~~Use actual passwords~~ Now it uses hashed passwords with bcrypt
* ~~Validate form data~~ Now validates with WTForms
* ~~Design permission system (general admin, group admin, machine permissions)~~ Flask Security provides role management
* Settings file
* Logging
* Single member edit page
* Admin to give member's permissions and roles / admin can see which members are not yet confirmed, their inscription date and confirm or delete them
* aetelbot integration

## Other To-Do's:
* Email group function
* AETEL meeting minutes generation & management
* Space & tool reservation
* Workshops & formation management
* aetelbot management page
* MQTT command zapper

* Groups for projects, training, current year members
* List groups
* Create new groups
* Add people to groups

### Application Notes:
Implemented with Python, Flask, SQLite and Spectre.

¡cutrenet vive, la lucha sigue!