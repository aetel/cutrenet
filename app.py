#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, flash, redirect, render_template, request, session, abort, Response, send_from_directory, url_for
from flask_security import Security, login_required, \
     SQLAlchemySessionUserDatastore, current_user, roles_required
from flask_mail import Mail, Message
from database import db_session
from models import User, Role, Tool, Workshop
from forms import ExtendedRegisterForm, EmailForm
from functions.email import email_all
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# Create app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = os.urandom(16)
app.config['SECURITY_PASSWORD_SALT'] = '/2aX16zPnnIgfMwkOjGX4S'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_CONFIRMABLE'] = False
app.config['SECURITY_TRACKABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = True
# makes password recoverable via /reset
app.config['SECURITY_RECOVERABLE'] = True

# Mail config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'test@gmail.com'
app.config['MAIL_PASSWORD'] = 'pass'
mail = Mail(app)

# File Upload
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Setup Flask-Security
user_datastore = SQLAlchemySessionUserDatastore(db_session,
                                                User, Role)
security = Security(app, user_datastore, register_form=ExtendedRegisterForm)

# Create a user to test with


@app.before_first_request
def create_user():
    pass

# Views


@app.route('/')
def home():
    return render_template('index.html', title='cutrenet')

# send email to all members


@app.route('/mail', methods=['POST', 'GET'])
@login_required
@roles_required('admin')
def mass_mail():
    form = EmailForm()
    if request.method == 'GET':
        return render_template('email.html', form=form, title='cutrenet')
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.attachment.data:
                f = form.attachment.data
                filename = secure_filename(f.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                f.save(file_path)
                email_all(app, mail, request.form, filename)
            else:
                email_all(app, mail, request.form,'')
            flash(u'Correo enviado a todos los miembros', 'success')
            if file_path:
                os.remove(file_path)
        return render_template('email.html', form=form, title='cutrenet')


# user profile page
@app.route('/profile')
@login_required
def member_profile():
    result = db_session.query(User).filter_by(id=session["user_id"]).first()
    db_session.commit()
    return render_template('profile.html', result=result, title='cutrenet', subtitle=current_user.first_name + ' ' + current_user.last_name)

# this is when user clicks edit link


@app.route('/profile/edit', methods=['GET'])
@login_required
def select_edit_member_profile():
    eresult = None
    edni = request.args.get('edni')
    if current_user.has_role('admin') or current_user.dni == edni:
        if request.method == 'GET':
            eresult = db_session.query(User).filter_by(dni=edni).first()
        results = db_session.query(User).all()
        db_session.commit()
        form = ExtendedRegisterForm()
        del form.password                   # Quitamos el campo de la contraseña del formulario
        del form.password_confirm
        return render_template('profile.html', form=form, result=eresult, results=results, title='cutrenet', subtitle='miembros')
    else:
        flash(u'No tienes permisos para editar ese miembro', 'error')
        return render_template('403.html', title='cutrenet', subtitle='403'), 403

# imitate this for edit profile page & email


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required.')
            return render_template('contact.html', form=form)
        else:
            return render_template('success.html')
    elif request.method == 'GET':
        return render_template('contact.html', form = form)

# or this
@app.route('/registeroo', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.username.data, form.email.data,
                    form.password.data)
        db_session.add(user)
        flash('Thanks for registering')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

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

# this is when Treasurer clicks confirm link
@app.route('/members/confirm', methods=['POST', 'GET'])
@login_required
@roles_required('admin')
def confirm_member():
    if request.method == 'GET':
        dni = request.args.get('dni')
        user = db_session.query(User).filter_by(dni=dni).first()
        # user.active = not user.active
        member_role = user_datastore.find_or_create_role(name='member', description='Miembro Activo')
        if user.has_role(member_role):
            user_datastore.remove_role_from_user(user, member_role)
            flash(u'Desconfirmado satisfactoriamente', 'alert')
        else:
            user_datastore.add_role_to_user(user, member_role)
            flash(u'Confirmado satisfactoriamente', 'success')
    results = db_session.query(User).all()
    db_session.commit()
    return render_template('database.html', results=results, title='cutrenet', subtitle='miembros')

# this is when Admin clicks give admin link
@app.route('/members/admin', methods=['POST', 'GET'])
@login_required
@roles_required('admin')
def give_admin():
    if request.method == 'GET':
        dni = request.args.get('dni')
        user = db_session.query(User).filter_by(dni=dni).first()
        # user.active = not user.active
        admin_role = user_datastore.find_or_create_role(name='admin', description='Administrator')
        if user.has_role(admin_role):
            user_datastore.remove_role_from_user(user, admin_role)
            flash(u'Rol de ADMINISTRADOR retirado satisfactoriamente', 'alert')
        else:
            user_datastore.add_role_to_user(user, admin_role)
            flash(u'Rol de ADMINISTRADOR asignado satisfactoriamente', 'success')
    results = db_session.query(User).all()
    db_session.commit()
    return render_template('database.html', results=results, title='cutrenet', subtitle='miembros')

@app.route('/workshops')
def list_workshops():
    #results = select([workshops]).order_by(workshops.c.date.desc())
    results = db_session.query(Workshop).order_by(Workshop.date.desc())
    #workshops = db_session.query(Workshop)
    #results = workshops.order_by(Workshop.date.desc())
    #results = db_session.query(Workshop).order_by(db_session.date.desc()).limit(3).all()
    return render_template('workshops.html', results=results, title='cutrenet', subtitle='talleres')

@app.route('/tools')
@login_required
def list_tools():
    results = db_session.query(Tool).all()
    db_session.commit()
    return render_template('tool_list.html', results=results, title='cutrenet', subtitle='herramientas')

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
