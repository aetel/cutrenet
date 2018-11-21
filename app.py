#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, flash, redirect, render_template, request, session, abort, Response
from flask_security import Security, login_required, \
     SQLAlchemySessionUserDatastore, current_user, roles_required
from database import db_session
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
#app.config['SECURITY_RECOVERABLE'] = True #makes password recoverable via /reset

# Setup Flask-Security
user_datastore = SQLAlchemySessionUserDatastore(db_session,
                                                User, Role)
security = Security(app, user_datastore,register_form=ExtendedRegisterForm)

# Create a user to test with
@app.before_first_request
def create_user():
    pass

# Views
@app.route('/')
def home():
    return render_template('index.html', title='cutrenet')

# user profile page
@app.route('/profile')
@login_required
def member_profile():
    result = db_session.query(User).filter_by(id=session["user_id"]).first()
    db_session.commit()
    return render_template('profile.html', result=result, title='cutrenet', subtitle=current_user.first_name+' '+current_user.last_name)

# this is when user clicks edit link
@app.route('/profile/edit', methods=['GET'])
@login_required
def select_edit_member_profile():
    eresult = None
    edni = request.args.get('edni')
    if current_user.has_role('admin') or current_user.dni==edni:
        if request.method == 'GET':
            eresult = db_session.query(User).filter_by(dni=edni).first()
        results = db_session.query(User).all()
        db_session.commit()
        form = ExtendedRegisterForm()
        del form.password                   # Quitamos el campo de la contraseña del formulario
        del form.password_confirm
        return render_template('profile.html', form = form, result=eresult, results=results, title='cutrenet', subtitle='miembros')
    else:
        flash(u'No tienes permisos para editar ese miembro', 'error')
        return render_template('403.html', title='cutrenet', subtitle='403'), 403


# this is when user sends edit form
@app.route('/profile/edit', methods=['POST'])
@login_required
def edit_member():
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
        flash(u'Editado satisfactoriamente', 'success')
    results = db_session.query(User).all()
    db_session.commit()
    if current_user.has_role('admin'): # Si el usuario es administrador le mandamos a la lista de miembros, si no a su perfil
        return render_template('database.html', results=results, title='cutrenet', subtitle='miembros')
    else:
        return redirect('/profile', code=302)

# this is when user clicks delete link
@app.route('/profile/delete', methods=['POST', 'GET'])
@login_required
def delete_profile():
    if request.method == 'GET':
        dni = request.args.get('dni')
        db_session.query(User).filter_by(dni=dni).delete()
        flash(u'Borrado satisfactoriamente', 'success')
    results = db_session.query(User).all()
    db_session.commit()
    if current_user.has_role('admin'): # Si el usuario es administrador le mandamos a la lista de miembros, si no a su perfil
        return render_template('database.html', results=results, title='cutrenet', subtitle='miembros')
    else:
        return redirect('/', code=302)
        
# members list
@app.route('/members')
@login_required
@roles_required('admin')
def member_database():
    results = db_session.query(User).all()
    db_session.commit()
    return render_template('database.html', results=results, title='cutrenet', subtitle='miembros')

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

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    flash(u'Deslogueado satisfactoriamente', 'normal')
    return redirect('login', code=302, title='cutrenet')

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html', title='cutrenet', subtitle='404'), 404

if __name__ == '__main__':
    app.run()