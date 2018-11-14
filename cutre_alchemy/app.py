from flask import Flask, flash, redirect, render_template, request, session, abort, Response
from flask_security import Security, login_required, \
     SQLAlchemySessionUserDatastore
from database import db_session, init_db
from models import User, Role
from forms import ExtendedRegisterForm
import os

# Create app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = os.urandom(16)
app.config['SECURITY_PASSWORD_SALT'] = '/2aX16zPnnIgfMwkOjGX4S'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_CONFIRMABLE'] = False
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
# Mail config. Place after 'Create app'
# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 465
# app.config['MAIL_USE_SSL'] = True
# app.config['MAIL_USERNAME'] = 'shit.to.test@gmail.com'
# app.config['MAIL_PASSWORD'] = ''
# mail = Mail(app)

# Setup Flask-Security
user_datastore = SQLAlchemySessionUserDatastore(db_session,
                                                User, Role)
security = Security(app, user_datastore,register_form=ExtendedRegisterForm)

# Create a user to test with
@app.before_first_request
def create_user():
    pass
    #init_db()
    #user_datastore.create_user(email='admin@example.com', password='admin')
    #db_session.commit()

# Views
@app.route('/')
@login_required
def member_database():
    results = db_session.query(User).all()
    print(results)
    return render_template('database.html', results=results)

# this is when user clicks edit link
@app.route('/query_edit', methods=['POST', 'GET'])
@login_required
def sql_editlink():
    if request.method == 'GET':
        edni = request.args.get('edni')
        eresults = sql_query(
            ''' SELECT * FROM data_table where dni = ? ''', (edni,))
    results = sql_query(''' SELECT * FROM data_table''')
    return render_template('database.html', eresults=eresults, results=results)

# this is when user clicks delete link
@app.route('/delete', methods=['POST', 'GET'])
@login_required
def sql_datadelete():
    from functions.sqlquery import sql_delete, sql_query
    if request.method == 'GET':
        dni = request.args.get('dni')
        sql_delete(''' DELETE FROM data_table where dni = ?''', (dni,))
        flash(u'Borrado satisfactoriamente', 'success')
    results = sql_query(''' SELECT * FROM data_table''')
    msg = 'DELETE FROM data_table WHERE dni = ' + dni
    return render_template('database.html', results=results, msg=msg)


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    flash(u'Deslogueado satisfactoriamente', 'normal')
    return redirect('login', code=302)

if __name__ == '__main__':
    app.run()