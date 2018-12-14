#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, flash, redirect, render_template, request, session, abort, Response, send_from_directory, url_for
from flask_security import Security, login_required, \
     SQLAlchemySessionUserDatastore, current_user, roles_required
from flask_mail import Mail, Message
from database import db_session
from models import User, Role, Tool, Workshop
from forms import ExtendedRegisterForm, EmailForm, ToolForm, EditMemberForm
from functions.email import email_all
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = 'static/uploads'
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
app.config['MAIL_USERNAME'] = 'aetel.backend@gmail.com'
app.config['MAIL_PASSWORD'] = 'drm3ngu3ch3'
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
                os.remove(file_path)
            else:
                email_all(app, mail, request.form,'')
            flash(u'Correo enviado a todos los miembros', 'success')
        return render_template('email.html', form=form, title='cutrenet')


# user profile page
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def member_profile():
    if request.method == 'GET':
        if 'dni' in request.args:
            dni = request.args.get('dni')
            user = db_session.query(User).filter_by(dni=dni).first()
            return render_template('profile.html', result=user, title='cutrenet', subtitle=user.first_name + ' ' + user.last_name)
        elif 'edit' in request.args:
            dni = request.args.get('edit')
            user = db_session.query(User).filter_by(dni=dni).first()
            if int(session["user_id"]) == int(user.id) or current_user.has_role('admin'):
                form = EditMemberForm(self_edit_dni=dni,self_edit_email=user.email)
                return render_template('profile.html', form=form, result=user, title='cutrenet', subtitle=user.first_name + ' ' + user.last_name)
            else:
                flash(u'No tienes permisos para editar este perfil', 'error')
                return redirect('/', code=302)
        elif 'delete' in request.args and current_user.has_role('admin'):
            dni = request.args.get('delete')
            db_session.query(User).filter_by(dni=dni).delete()
            db_session.commit()
            flash(u'Perfil borrado', 'success')
            if current_user.has_role('admin'): # Si el usuario es administrador le mandamos a la lista de miembros, si no al inicio
                results = db_session.query(User).all()
                return render_template('profile_list.html', results=results, title='cutrenet', subtitle='miembros')
            else:
                return redirect('/', code=302)
        elif not current_user.has_role('admin'):
            flash(u'No tienes permisos para editar este perfil', 'error')
            return redirect('/', code=302)
        else:
            flash(u'Tienes que seleccionar un perfil', 'error')
            results = db_session.query(User).all()
            return render_template('profile_list.html', results=results, title='cutrenet', subtitle='miembros')

    if request.method == 'POST' and current_user.has_role('admin'):
        if 'edit' in request.args:
            dni = request.args.get('edit')
            user = db_session.query(User).filter_by(dni=dni).first()
            form = EditMemberForm(self_edit_dni=dni,self_edit_email=user.email)
            print('Nombre: '+request.form['first_name'])
            if form.validate() == True:
                print('Nombre: '+request.form['first_name'])
                user.last_name = request.form['last_name']
                user.first_name = request.form['first_name']
                user.email = request.form['email']
                user.dni = request.form['dni']
                user.school = request.form['school']
                user.degree = request.form['degree']
                user.year = request.form['year']
                user.telegram = request.form['telegram']
                db_session.commit()
                flash(u'Perfil editado', 'success')
            if form.validate() == False:
                print('Nombre: '+request.form['first_name']+'NO')
                flash(u'Error al editar', 'error')
            return render_template('profile.html', form=form, result=user, title='cutrenet', subtitle=user.first_name + ' ' + user.last_name)


# members list
@app.route('/members', methods=['GET'])
@login_required
@roles_required('admin')
def member_database():
    if 'confirm' in request.args:
        dni = request.args.get('confirm')
        user = db_session.query(User).filter_by(dni=dni).first()
        if user.has_role('member'):
            user_datastore.remove_role_from_user(user, 'member')
            flash(u'Desconfirmado satisfactoriamente', 'alert')
        else:
            user_datastore.add_role_to_user(user, 'member')
            flash(u'Confirmado satisfactoriamente', 'success')
        db_session.commit()
    if 'admin' in request.args:
        dni = request.args.get('admin')
        user = db_session.query(User).filter_by(dni=dni).first()
        if user.has_role('admin'):
            user_datastore.remove_role_from_user(user, 'admin')
            flash(u'Rol de ADMINISTRADOR retirado satisfactoriamente', 'alert')
        else:
            user_datastore.add_role_to_user(user, 'admin')
            flash(u'Rol de ADMINISTRADOR asignado satisfactoriamente', 'success')
        db_session.commit()
    results = db_session.query(User).all()
    return render_template('profile_list.html', results=results, title='cutrenet', subtitle='miembros')


@app.route('/workshops')
def list_workshops():
    results = db_session.query(Workshop).order_by(Workshop.date.asc())
    instructors = db_session.query(User)
    return render_template('workshop_list.html', results=results, instructors=instructors, title='cutrenet', subtitle='talleres')


@app.route('/workshop', methods=['POST', 'GET'])
def view_workshop():
    if request.method == 'GET':
        if 'name' in request.args:
            name = request.args.get('name')
            result = db_session.query(Workshop).filter_by(name=name).first()
            return render_template('workshop.html', result=result, title='cutrenet', subtitle=name)
        elif not current_user.has_role('admin'):
            flash(u'No tienes permisos para editar esta herramienta', 'error')
            return redirect('/tools', code=302)
        elif 'add' in request.args:
            form = ToolForm()
            return render_template('tool.html', form=form, title='cutrenet', subtitle="new tool")
        elif 'edit' in request.args:
            ename = request.args.get('edit')
            form = ToolForm(self_edit=ename)
            result = db_session.query(Workshop).filter_by(name=ename).first()
            form.description.data = result.description # Prepopulate textarea with past information, can´t do it at render time
            return render_template('tool.html', form=form, result=result, title='cutrenet', subtitle=ename)
        elif 'delete_img' in request.args:
            del_img = request.args.get('delete_img')
            tool = db_session.query(Workshop).filter_by(name=del_img).first()
            if tool.image:
                os.remove(tool.image) # Delete old image
                tool.image = None
                db_session.commit()
                flash(u'Imagen eliminada', 'success')
            else:
                flash(u'No hay imagen que eliminar', 'alert')
            return render_template('tool.html', result=tool, title='cutrenet', subtitle=tool.name)
        elif 'delete' in request.args:
            delete = request.args.get('delete')
            tool = db_session.query(Workshop).filter_by(name=delete).first()
            db_session.delete(tool)
            db_session.commit()
            flash(u'Herramienta eliminada', 'success')
            return redirect('/tools', code=302)
        else:
            flash(u'Tienes que seleccionar una herramienta', 'error')
            return redirect('/tools', code=302)

    if request.method == 'POST' and current_user.has_role('admin'):
        if 'edit' in request.args:
            ename = request.args.get('edit')
            tool = db_session.query(Workshop).filter_by(name=ename).first()
            form = ToolForm(self_edit=ename)
            if form.validate_on_submit():
                tool.name = request.form['name']
                tool.description = request.form['description']
                tool.location = request.form['location']
                tool.manual = request.form['manual']
                tool.documentation = request.form['documentation']

                if form.image.data:
                    if tool.image is not None:
                        os.remove(tool.image) # Delete old image
                    f = form.image.data
                    filename = secure_filename(f.filename)
                    directory = app.config['UPLOAD_FOLDER']+'/tools'
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    file_path = os.path.join(directory, filename)
                    f.save(file_path)
                    tool.image = file_path # Save the file path of the Tool image in the database

                db_session.commit()
                flash(u'Herramienta editada', 'success')
            return render_template('tool.html', form=form, result=tool, title='cutrenet', subtitle=tool.name)
        elif 'add' in request.args:
            name = request.args.get('add')
            tool = Tool()
            form = ToolForm()
            if form.validate_on_submit():
                tool.name = request.form['name']
                tool.description = request.form['description']
                tool.location = request.form['location']
                tool.manual = request.form['manual']
                tool.documentation = request.form['documentation']

                if form.image.data:
                    if tool.image is not None:
                        os.remove(tool.image) # Delete old image
                    f = form.image.data
                    filename = secure_filename(f.filename)
                    directory = app.config['UPLOAD_FOLDER']+'/tools'
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    file_path = os.path.join(directory, filename)
                    f.save(file_path)
                    tool.image = file_path # Save the file path of the Tool image in the database

                db_session.add(tool)
                db_session.commit()
                flash(u'Herramienta añadida', 'success')
                return redirect('tools', code=302)
            return render_template('tool.html', form=form, result=tool, title='cutrenet', subtitle=tool.name)


@app.route('/tools')
def list_tools():
    results = db_session.query(Tool).all()
    db_session.commit()
    return render_template('tool_list.html', results=results, title='cutrenet', subtitle='herramientas')


@app.route('/tool', methods=['POST', 'GET'])
def view_tool():
    if request.method == 'GET':
        if 'name' in request.args:
            name = request.args.get('name')
            result = db_session.query(Tool).filter_by(name=name).first()
            return render_template('tool.html', result=result, title='cutrenet', subtitle=name)
        elif not current_user.has_role('admin'):
            flash(u'No tienes permisos para editar esta herramienta', 'error')
            return redirect('/tools', code=302)
        elif 'add' in request.args:
            form = ToolForm()
            return render_template('tool.html', form=form, title='cutrenet', subtitle="new tool")
        elif 'edit' in request.args:
            ename = request.args.get('edit')
            form = ToolForm(self_edit=ename)
            result = db_session.query(Tool).filter_by(name=ename).first()
            form.description.data = result.description # Prepopulate textarea with past information, can´t do it at render time
            return render_template('tool.html', form=form, result=result, title='cutrenet', subtitle=ename)
        elif 'delete_img' in request.args:
            del_img = request.args.get('delete_img')
            tool = db_session.query(Tool).filter_by(name=del_img).first()
            if tool.image:
                os.remove(tool.image) # Delete old image
                tool.image = None
                db_session.commit()
                flash(u'Imagen eliminada', 'success')
            else:
                flash(u'No hay imagen que eliminar', 'alert')
            return render_template('tool.html', result=tool, title='cutrenet', subtitle=tool.name)
        elif 'delete' in request.args:
            delete = request.args.get('delete')
            tool = db_session.query(Tool).filter_by(name=delete).first()
            db_session.delete(tool)
            db_session.commit()
            flash(u'Herramienta eliminada', 'success')
            return redirect('/tools', code=302)
        else:
            flash(u'Tienes que seleccionar una herramienta', 'error')
            return redirect('/tools', code=302)

    if request.method == 'POST' and current_user.has_role('admin'):
        if 'edit' in request.args:
            ename = request.args.get('edit')
            tool = db_session.query(Tool).filter_by(name=ename).first()
            form = ToolForm(self_edit=ename)
            if form.validate_on_submit():
                tool.name = request.form['name']
                tool.description = request.form['description']
                tool.location = request.form['location']
                tool.manual = request.form['manual']
                tool.documentation = request.form['documentation']

                if form.image.data:
                    if tool.image is not None:
                        os.remove(tool.image) # Delete old image
                    f = form.image.data
                    filename = secure_filename(f.filename)
                    directory = app.config['UPLOAD_FOLDER']+'/tools'
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    file_path = os.path.join(directory, filename)
                    f.save(file_path)
                    tool.image = file_path # Save the file path of the Tool image in the database

                db_session.commit()
                flash(u'Herramienta editada', 'success')
            return render_template('tool.html', form=form, result=tool, title='cutrenet', subtitle=tool.name)
        elif 'add' in request.args:
            name = request.args.get('add')
            tool = Tool()
            form = ToolForm()
            if form.validate_on_submit():
                tool.name = request.form['name']
                tool.description = request.form['description']
                tool.location = request.form['location']
                tool.manual = request.form['manual']
                tool.documentation = request.form['documentation']

                if form.image.data:
                    if tool.image is not None:
                        os.remove(tool.image) # Delete old image
                    f = form.image.data
                    filename = secure_filename(f.filename)
                    directory = app.config['UPLOAD_FOLDER']+'/tools'
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    file_path = os.path.join(directory, filename)
                    f.save(file_path)
                    tool.image = file_path # Save the file path of the Tool image in the database

                db_session.add(tool)
                db_session.commit()
                flash(u'Herramienta añadida', 'success')
                return redirect('tools', code=302)
            return render_template('tool.html', form=form, result=tool, title='cutrenet', subtitle=tool.name)


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
