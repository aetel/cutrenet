# cutrenet
This is a simple Python CRUD application to manage AETEL members.

# STILL IN DEVELOPMENT

## Use:
Launch setup.py, if a database exists it will use that, if not it will create one.
When database is fresh it creates a user admin@example.com/admin.
Then launch the main python script.
Go to /register?new_member to register a new member.

## To-Do:
* ~~Use actual passwords~~ Now it uses hashed passwords with argon2
* ~~Validate form data~~ Now validates with HTML5 and some JavaScript
* Design permission system (general admin, group admin, machine permissions)
* Single member edit page
* aetelbot integration
* Groups for projects, training, current year members
* List groups
* Create new groups
* Add people to groups


## Other To-Do's:
* Email group function
* AETEL meeting minutes generation & management
* Space & tool reservation
* Workshops & formation management
* aetelbot management page
* MQTT command zapper


### Application Notes:
Implemented with Ptyhon, Flask, SQLite and bootstrap.

¡cutrenet vive, la lucha sigue!