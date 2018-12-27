#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, flash, redirect, render_template, request, session, abort, Response, send_from_directory, url_for
from flask_security import Security, login_required, \
     SQLAlchemySessionUserDatastore, current_user, roles_required, \
     logout_user
from flask_mail import Mail, Message
from database import db_session
from models import User, Role, Tool, Workshop, WorkshopsUsers, Voting, Option, VotesUsers
from forms import ExtendedRegisterForm, EmailForm, ToolForm, EditMemberForm, WorkshopForm, VotingForm, VoteForm
from functions.email import email_all
from werkzeug.utils import secure_filename
from datetime import date, timedelta
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
app.config['MAIL_PASSWORD'] = 'backtheend'
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
    session['url'] = request.url[len(request.url_root):]
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
            if current_user.dni == dni or current_user.has_role('admin'):
                user = db_session.query(User).filter_by(dni=dni).first()
                workshops = db_session.query(WorkshopsUsers).join(Workshop).filter(User.dni == dni)
            else:
                flash(u'No tienes permisos para ver este perfil', 'error')
            return render_template('profile.html', result=user, title='cutrenet', workshops=workshops, subtitle=user.first_name + ' ' + user.last_name)
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
            if current_user.dni == dni or current_user.has_role('admin'):
                db_session.query(User).filter_by(dni=dni).delete()
                db_session.commit()
                flash(u'Perfil borrado', 'success')
            else:
                flash(u'No tienes permisos para borrar este perfil', 'error')
            if current_user.has_role('admin'): # Si el usuario es administrador le mandamos a la lista de miembros, si no al inicio
                results = db_session.query(User).all()
                return render_template('profile_list.html', results=results, title='cutrenet', subtitle='miembros')
            else:
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
    session['url'] = request.url[len(request.url_root):]
    results = db_session.query(Workshop).order_by(Workshop.date.asc())
    return render_template('workshop_list.html', results=results, title='cutrenet', subtitle='talleres')


@app.route('/workshop', methods=['POST', 'GET'])
def view_workshop():
    session['url'] = request.url[len(request.url_root):]
    if request.method == 'GET':
        enlisted = {}
        if 'id' in request.args:
            uid = request.args.get('id')
            workshop = db_session.query(Workshop).filter_by(id=uid).first()
            enlisted['number'] = db_session.query(WorkshopsUsers).filter_by(workshop_id=workshop.id).count()
            enlisted['list'] = User.query.filter(User.workshops.any(id=workshop.id)).all()

            # Check if user is already enlisted. 1 for enlisted, 0 for not enlisted, 2 for not logged in
            if current_user.is_authenticated:
                enlisted['user'] = db_session.query(WorkshopsUsers).filter_by(workshop_id=workshop.id).filter_by(user_id=current_user.id).count()
            else:
                enlisted['user'] = 2
            return render_template('workshop.html', result=workshop, enlisted=enlisted, title='cutrenet', subtitle=workshop.name)
        elif current_user.is_authenticated and 'enlist' in request.args:
            workshop_id = request.args.get('enlist')
            workshop = db_session.query(Workshop).filter_by(id=workshop_id).first()
            user = db_session.query(User).filter_by(id=current_user.id).first()

            enlisted['number'] = db_session.query(WorkshopsUsers).filter_by(workshop_id=workshop.id).count()

            if workshop.participants > enlisted['number']:
                if workshop.members_only and not user.has_role('member'):
                    flash(u'Este taller es solo para miembros', 'error')
                else:
                    workshop.users.append(user)
                    db_session.commit()
                    flash(u'Inscrito en el taller', 'success')
            else:
                flash(u'El taller está lleno', 'alert')

            if current_user.is_authenticated:
                enlisted['user'] = db_session.query(WorkshopsUsers).filter_by(workshop_id=workshop.id).filter_by(user_id=current_user.id).count()
            else:
                enlisted['user'] = 2
            enlisted['number'] = db_session.query(WorkshopsUsers).filter_by(workshop_id=workshop.id).count()
            enlisted['list'] = User.query.filter(User.workshops.any(id=workshop.id)).all()
            return render_template('workshop.html', result=workshop, enlisted=enlisted, title='cutrenet', subtitle=workshop.name)
        elif current_user.is_authenticated and 'unenlist' in request.args:
            workshop_id = request.args.get('unenlist')
            workshop = db_session.query(Workshop).filter_by(id=workshop_id).first()
            
            if current_user.is_authenticated:
                enlisted['user'] = db_session.query(WorkshopsUsers).filter_by(workshop_id=workshop_id).filter_by(user_id=current_user.id).count()
            else:
                enlisted['user'] = 2

            if enlisted['user'] == 1:
                user = db_session.query(User).filter_by(id=current_user.id).first()
                workshop.users.remove(user)
                db_session.commit()
                enlisted['user'] = 0
                flash(u'Desinscrito en el taller', 'alert')
            else:
                flash(u'El usuario no está inscrito en el taller', 'error')

            enlisted['number'] = db_session.query(WorkshopsUsers).filter_by(workshop_id=workshop_id).count()
            enlisted['list'] = User.query.filter(User.workshops.any(id=workshop_id)).all()
            return render_template('workshop.html', result=workshop, enlisted=enlisted, title='cutrenet', subtitle=workshop.name)
        elif not current_user.has_role('admin'):
            flash(u'No tienes permisos para editar este taller', 'error')
            return redirect('/workshops', code=302)
        elif 'add' in request.args:
            form = WorkshopForm()
            return render_template('workshop.html', form=form, title='cutrenet', subtitle="new tool")
        elif 'edit' in request.args:
            eid = request.args.get('edit')
            form = WorkshopForm()
            result = db_session.query(Workshop).filter_by(id=eid).first()
            form.description.data = result.description # Prepopulate fields with past information, can´t do it at render time
            form.members_only.data = result.members_only
            form.instructor.data = result.instructor.dni
            return render_template('workshop.html', form=form, result=result, title='cutrenet', subtitle=result.name)
        elif 'delete_img' in request.args:
            del_img = request.args.get('delete_img')
            workshop = db_session.query(Workshop).filter_by(id=del_img).first()
            if tool.image:
                os.remove(tool.image) # Delete old image
                tool.image = None
                db_session.commit()
                flash(u'Imagen eliminada', 'success')
            else:
                flash(u'No hay imagen que eliminar', 'alert')
            return render_template('workshop.html', result=tool, title='cutrenet', subtitle=tool.name)
        elif 'delete' in request.args:
            delete = request.args.get('delete')
            workshop = db_session.query(Workshop).filter_by(name=delete).first()
            db_session.delete(workshop)
            db_session.commit()
            flash(u'Taller eliminado', 'success')
            return redirect('/workshops', code=302)
        else:
            flash(u'Tienes que seleccionar un taller', 'error')
            return redirect('/workshops', code=302)

    if request.method == 'POST' and current_user.has_role('admin'):
        if 'edit' in request.args:
            eid = request.args.get('edit')
            workshop = db_session.query(Workshop).filter_by(id=eid).first()
            form = WorkshopForm()
            if form.validate_on_submit():
                workshop.name = request.form['name']
                workshop.description = request.form['description']
                workshop.location = request.form['location']
                workshop.date = form.date.data
                workshop.participants = int(request.form['participants'])
                workshop.members_only = form.members_only.data

                instructor = db_session.query(User).filter_by(dni=request.form['instructor']).first()
                if instructor is not None:
                    instructor.workshop_instructor.append(workshop)
                tool = db_session.query(Tool).filter_by(id=request.form['tooling']).first()
                if tool is not None:
                    tool.workshops.append(workshop)

                if form.image.data:
                    if workshop.image is not None:
                        os.remove(tool.image) # Delete old image
                    f = form.image.data
                    filename = secure_filename(f.filename)
                    directory = app.config['UPLOAD_FOLDER']+'/workshops'
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    file_path = os.path.join(directory, filename)
                    f.save(file_path)
                    tool.image = file_path # Save the file path of the Tool image in the database

                db_session.commit()
                flash(u'Taller editado', 'success')
            return render_template('workshop.html', form=form, result=workshop, title='cutrenet', subtitle=workshop.name)
        elif 'add' in request.args:
            name = request.args.get('add')
            workshop = Workshop()
            form = WorkshopForm()
            if form.validate_on_submit():
                workshop.name = request.form['name']
                workshop.description = request.form['description']
                workshop.location = request.form['location']
                workshop.date = form.date.data
                workshop.participants = int(request.form['participants'])
                workshop.members_only = form.members_only.data

                instructor = db_session.query(User).filter_by(dni=request.form['instructor']).first()
                if instructor is not None:
                    instructor.workshop_instructor.append(workshop)
                tool = db_session.query(Tool).filter_by(id=request.form['tooling']).first()
                if tool is not None:
                    tool.workshops.append(workshop)

                if form.image.data:
                    if tool.image is not None:
                        os.remove(tool.image) # Delete old image
                    f = form.image.data
                    filename = secure_filename(f.filename)
                    directory = app.config['UPLOAD_FOLDER']+'/workshops'
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    file_path = os.path.join(directory, filename)
                    f.save(file_path)
                    tool.image = file_path # Save the file path of the Tool image in the database

                db_session.add(workshop)
                db_session.commit()
                flash(u'Taller añadido', 'success')
                return redirect('workshops', code=302)
            return render_template('workshop.html', form=form, result=workshop, title='cutrenet', subtitle=workshop.name)


@app.route('/tools')
def list_tools():
    session['url'] = request.url[len(request.url_root):]
    results = db_session.query(Tool).all()
    db_session.commit()
    return render_template('tool_list.html', results=results, title='cutrenet', subtitle='herramientas')


@app.route('/tool', methods=['POST', 'GET'])
def view_tool():
    session['url'] = request.url[len(request.url_root):]
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
            form.maintainer.data = result.maintainer.dni
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

                maintainer = db_session.query(User).filter_by(dni=request.form['maintainer']).first()
                if maintainer is not None:
                    maintainer.tool_maintainer.append(tool)

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
            tool = Tool()
            form = ToolForm()
            if form.validate_on_submit():
                tool.name = request.form['name']
                tool.description = request.form['description']
                tool.location = request.form['location']
                tool.manual = request.form['manual']
                tool.documentation = request.form['documentation']

                maintainer = db_session.query(User).filter_by(dni=request.form['maintainer']).first()
                if maintainer is not None:
                    maintainer.tool_maintainer.append(tool)

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
            return render_template('tool.html', form=form, title='cutrenet', subtitle="new tool")

@app.route('/votaciones')
@login_required
@roles_required('member')
def list_votings():
    session['url'] = request.url[len(request.url_root):]
    results = db_session.query(Voting).all()
    db_session.commit()
    today = date.today() - timedelta(1)
    return render_template('voting_list.html', results=results, today=today, title='cutrenet', subtitle='votaciones')

@app.route('/votacion', methods=['POST', 'GET'])
@login_required
@roles_required('member')
def view_voting():
    session['url'] = request.url[len(request.url_root):]
    votes = {}
    if request.method == 'GET':
        if 'id' in request.args:
            uid = request.args.get('id')
            result = db_session.query(Voting).filter_by(id=uid).first()

            form = VoteForm()
            options = db_session.query(Option).filter_by(voting_id=uid).all()
            choices = []
            votes['number'] = {}
            votes['user'] = 0
            for option in options:
                choices.append((option.id, option.name))
                votes['number'][option.name] = db_session.query(VotesUsers).filter_by(option_id=option.id).count()
                votes['user'] += db_session.query(VotesUsers).filter_by(option_id=option.id).filter_by(user_id=current_user.id).count()
            form.option.choices = choices

            if result.end_date + timedelta(1) > date.today(): #bigger means older
                votes['end'] = 0
            else:
                votes['end'] = 1

            return render_template('voting.html', result=result, form=form, votes=votes, title='cutrenet', subtitle=result.name)
        elif not current_user.has_role('admin'):
            flash(u'No tienes permisos para añadir o borrar votaciones', 'error')
            return redirect('/votaciones', code=302)
        elif 'add' in request.args:
            form = VotingForm()
            return render_template('voting.html', form=form, title='cutrenet', subtitle="new tool")
        elif 'delete' in request.args:
            delete = request.args.get('delete')
            voting = db_session.query(Voting).filter_by(id=delete).first()
            db_session.delete(voting)
            db_session.commit()
            flash(u'Votación eliminada', 'success')
            return redirect('/votaciones', code=302)
        else:
            flash(u'Tienes que seleccionar una votación', 'error')
            return redirect('/votaciones', code=302)

    if request.method == 'POST':
        if 'add' in request.args and current_user.has_role('admin'):
            voting = Voting()
            form = VotingForm()
            if form.validate_on_submit():
                voting.name = request.form['name']
                voting.description = request.form['description']
                voting.start_date = form.start_date.data
                voting.end_date = form.end_date.data
                names = request.form['options'].split('|')

                for name in names:
                    option = Option()
                    option.name = name
                    voting.options.append(option)

                db_session.add(voting)
                db_session.commit()
                flash(u'Votación añadida', 'success')
                return redirect('votaciones', code=302)
            return render_template('voting.html', form=form, votes=votes, title='cutrenet', subtitle="new voting")
        elif 'vote' in request.args:
            uid = request.args.get('vote')
            form = VoteForm()
            options = db_session.query(Option).filter_by(voting_id=uid).all()
            choices = []
            votes['number'] = {}
            votes['user'] = 0
            for option in options:
                choices.append((option.id, option.name))
                votes['number'][option.name] = db_session.query(VotesUsers).filter_by(option_id=option.id).count()
                votes['user'] += db_session.query(VotesUsers).filter_by(option_id=option.id).filter_by(user_id=current_user.id).count()
            form.option.choices = choices

            result = db_session.query(Voting).filter_by(id=uid).first()
            if result.end_date + timedelta(1) > date.today(): #bigger means older
                votes['end'] = 0
            else:
                votes['end'] = 1
#            if form.validate_on_submit():
            if votes['user'] == 0:
                option = db_session.query(Option).filter_by(id=request.form['option']).first()
                user = db_session.query(User).filter_by(id=current_user.id).first()
                option.votes.append(user)
                db_session.add(option)
                db_session.commit()
                votes['user'] = 0
                for option in options:
                    votes['number'][option.name] = db_session.query(VotesUsers).filter_by(option_id=option.id).count()
                votes['user'] = 1
                flash(u'Voto registrado', 'success')
            else:
                flash(u'Ya has votado, mamón', 'alert')
            return render_template('voting.html', form=form, result=result, votes=votes, title='cutrenet', subtitle=u"voted ✔️")


@app.route('/change_password', methods=['POST', 'GET'])
def change_password():
    logout_user()
    return redirect('reset', code=302)


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    flash(u'Deslogueado satisfactoriamente', 'normal')
    return redirect('login', code=302, title='cutrenet')


@app.errorhandler(404)
def page_not_found(e):
    session['url'] = request.url[len(request.url_root):]
    # note that we set the 404 status explicitly
    return render_template('404.html', title='cutrenet', subtitle='404'), 404


if __name__ == '__main__':
    app.run()
