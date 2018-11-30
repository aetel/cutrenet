from models import User, Role
from flask_mail import Mail, Message
import os


def email_all(app,mail,data,attachment):
	users = User.query.filter(User.roles.any(Role.id.in_([2]))).all() # We pick the users that have role member (ID 2 in table roles)
	with mail.connect() as conn:
	    for user in users:
	        msg = Message(sender=("AETEL cutrenet", app.config['MAIL_USERNAME']),
	        			  recipients=[user.email],
	                      body=data['message'],
	                      subject=data['subject'])
	        if attachment:
	        	with app.open_resource(os.path.join(app.config['UPLOAD_FOLDER'],attachment)) as fp:
  					msg.attach(attachment, "image/png", fp.read())
	        conn.send(msg)