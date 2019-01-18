# cutrenet
This is a simple Python CRUD application to manage AETEL members, tools, workshops and more.

# STILL IN DEVELOPMENT

## To test it:
1. Clone this repo:
```bash
git clone https://github.com/aetel/cutrenet
```
2. Change directory:
```bash
cd cutrenet
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Launch setup.py, if a database exists it will use that, if not it will create one. When database is fresh it creates a user admin@example.com/admin:
```bash
python setup.py
```
5. Start the app:
```bash
python app.py
```
6. Go to your browser and navigate to 127.0.0.1:5000.

## To-Do:
* **Settings file:** Load settings from a specific file. Email server, webpage name, localised strings, aetelbot settings, sarao mode, etc
* **Logging:** Log relevant events
* **Admin notifications:** via email, telegram?
* **Add support for past members & granular admin rights:** Give past members a special role and stuff
* **Add main page with relevant information:** If plain user show info about workshops and calendar; if member show workshops, meeting minutes, tools, votes; if admin show everything.
* **Space & tool reservation:** ~~Tools have a page with relevant information such as: mantainer, documentation, manuals, picture, maintainer, etc. Admin can edit said pages.~~ Members can select a piece of equipment from a list and reserve it for a set time.
* **aetelbot integration & management page:** Generate confirmed members list. Edit aetelbot running directory. Edit aetelbot settings file.
* **AETEL meeting minutes generation & management:** Interface to input order of the day, date, hour, place of the meeting, presiding board and each of the points in markdown format; generates a JSON file with all data. View links to all generated minutes and links to a viewing page. Download in pdf.
* **Workshops & formation management:** ~~Admin can create a new workshop. Admin can choose if it's open for everyone or members only, number of people admitted and if it validates any tool usage. Users can join that workshop as long as there are free places. Admin can mark signed up users as paid and/or completed in the workshop page. Users who completed a workshop will show in their profiles. Admin can send an email to the users who signed up for a workshop or users that haven't paid. Show in profile managing workshops and participating workshops.~~
* **Voting:** ~~Admin can create new vote with title, time and options. Vote is open for set time. Members can select one of the options.~~
* **Email group function:** ~~Admin can send an email to all the members. Admin can send email with attachments to all members.~~

## Maybe?:
* **Log in with UPM account**
* **¿MQTT command zapper?** – Maybe too much complexity with no real use?
* Groups for projects, training, current year members
* List groups
* Create new groups
* Add people to groups

## ~~Joke~~ timeline:
* Finish implementing feature set
* Run over code and clean up and rewrite necessary parts
* Check variable names and change them where necessary to keep consistency
* Localise the whole app user side stuff in Spanish
* Check css to make it mobile friendly

### Application Notes:
Implemented with Python, Flask, SQLite and spectre.css

It's mandatory to install Flask-Security with _pip install git+https://github.com/mattupstate/flask-security_ or else [email won't work](https://github.com/mattupstate/flask-security/issues/685#ref-commit-241acf2)!

¡cutrenet vive, la lucha sigue!