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
* ~~Single member edit page~~ Now members can edit their profiles and admin can edit everyone – Need to add password update (leave as is if blank) and current password check in form
* Admin to give member's permissions and roles / admin can see which members are not yet confirmed, their inscription date and confirm or delete them
* aetelbot integration
* Add note about beta software and where to report bugs

## Other To-Do's:
* **Add main page with relevant information:** If plain user show info about workshops and calendar; if member show workshops, meeting minutes, tools, votes; if admin show everything.
* ~~**Email group function:** Admin can send an email to all the members.~~ Admin can send email with attachments to all members.
* **AETEL meeting minutes generation & management:** Interface to input order of the day, date, hour, place of the meeting, presiding board and each of the points in markdown format; generates a JSON file with all data. View links to all generated minutes and links to a viewing page. Download in pdf.
* **Space & tool reservation:** Tools have a page with relevant information such as: mantainer, documentation, manuals, etc. Admin can edit said pages. Members can select a piece of equipment from a list and reserve it for a set time.
* **Voting:** Admin can create new vote with title, time and options. Vote is open for set time. Members can select one of the options.
* **Workshops & formation management:** Admin can create a new workshop. Admin can choose if it's open for everyone or members only, number of people admitted and if it validates any tool usage. Users can join that workshop as long as there is free places. Admin can mark signed up users as paid and/or completed in the workshop page. Users who completed a workshop will show in their profiles. Admin can send an email to the users who signed up for a workshop.
* **aetelbot management page:** Generate confirmed members list. Edit aetelbot running directory. Edit aetelbot settings file.
* **¿MQTT command zapper?** – Maybe too much complexity with no real use?

* Groups for projects, training, current year members
* List groups
* Create new groups
* Add people to groups

### Application Notes:
Implemented with Python, Flask, SQLite and spectre.css

Install Flask-Security with pip install git+https://github.com/mattupstate/flask-security

¡cutrenet vive, la lucha sigue!