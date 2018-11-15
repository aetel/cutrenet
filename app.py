#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
app.config['SECURITY_TRACKABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False

# Setup Flask-Security
user_datastore = SQLAlchemySessionUserDatastore(db_session,
                                                User, Role)
security = Security(app, user_datastore,register_form=ExtendedRegisterForm)

# Create a user to test with
@app.before_first_request
def create_user():
    pass
    # init_db()
    # user_datastore.create_user(email='admin@example.com',
    #                      password='admin', dni=00000001A,
    #                      year=99, degree='AA', school='00',
    #                      first_name='Michael Ignatius',
    #                      last_name='Thomas Malloc',
    #                      telegram="aetelbot")
    # db_session.commit()

# Views
@app.route('/')
def home():
    return render_template('index.html', title='cutrenet')

@app.route('/members')
@login_required
def member_database():
    results = db_session.query(User).all()
    db_session.commit()
    return render_template('database.html', results=results, title='cutrenet', subtitle='miembros')

# this is when user clicks edit link
@app.route('/members/edit', methods=['GET'])
@login_required
def edit_member():
    eresult = None
    if request.method == 'GET':
        edni = request.args.get('edni')
        eresult = db_session.query(User).filter_by(dni=edni).first()
    results = db_session.query(User).all()
    db_session.commit()
    return render_template('database.html', eresult=eresult, results=results, title='cutrenet', subtitle='miembros')

@app.route('/members/edit', methods=['POST'], )
@login_required
def sql_dataedit():
    if request.method == 'POST':
        old_dni = request.form['old_dni']

        user = db_session.query(User).filter_by(dni=old_dni).first()
        user.last_name = request.form['last_name']
        user.first_name = request.form['first_name']
        user.email = request.form['email']
        user.dni = request.form['dni']
        user.school = request.form['school']
        user.degree = request.form['degree']
        user.year = request.form['year']
        user.telegram = request.form['telegram']
        user.password = request.form['password']
        flash(u'Editado satisfactoriamente', 'success')
    results = db_session.query(User).all()
    db_session.commit()
    return redirect('/members', code=302)

# this is when Treasurer clicks activate link
@app.route('/members/confirm', methods=['POST', 'GET'])
@login_required
def confirm_member():
    if request.method == 'GET':
        dni = request.args.get('dni')
        user = db_session.query(User).filter_by(dni=dni).first()
        user.active = not user.active
        flash(u'Confirmado satisfactoriamente', 'success')
    results = db_session.query(User).all()
    db_session.commit()
    return render_template('database.html', results=results, title='cutrenet', subtitle='miembros')

# this is when user clicks delete link
@app.route('/members/delete', methods=['POST', 'GET'])
@login_required
def delete_member():
    if request.method == 'GET':
        dni = request.args.get('dni')
        db_session.query(User).filter_by(dni=dni).delete()
        flash(u'Borrado satisfactoriamente', 'success')
    results = db_session.query(User).all()
    db_session.commit()
    return render_template('database.html', results=results, title='cutrenet', subtitle='miembros')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    flash(u'Deslogueado satisfactoriamente', 'normal')
    return redirect('login', code=302, title='cutrenet')

if __name__ == '__main__':
    app.run()