#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_security.forms import Form, RegisterForm, StringField, Required, validators
from wtforms import SelectField, TextAreaField, FileField, HiddenField, SubmitField,\
                    IntegerField, BooleanField, RadioField, ValidationError
from wtforms.fields.html5 import DateField
from database import db_session
from models import User, Tool, Voting
import json
from datetime import date, timedelta

from flask_security.utils import get_message

def json_choices_centros(file):
    with open(file) as f:
        data = json.load(f)
        choices = []
        for centro in data["datos"]:
            choices.append((centro['codigo'], centro['nombre']))
        return choices

def json_choices_planes(file):
    with open(file) as f:
        data = json.load(f)
        choices = []
        for centro in data["datos"]:
            for plan in data["datos"][centro]:
                choices.append((plan['codigo'], plan['nombre']))
        return choices

def choices_users():
    choices = []
    for user in db_session.query(User):
        choices.append((user.dni, user.first_name))
    return choices

def choices_tools():
    choices = []
    choices.append((0, 'No'))
    for tool in db_session.query(Tool):
        choices.append((tool.id, tool.name))
    return choices

def unique_user_dni(form, field):
    result = db_session.query(User).filter_by(dni=field.data).first()
    if result is not None and form.self_edit_dni.data != form.dni.data:
        msg = field.data+' ya tiene una cuenta asociada.'
        raise ValidationError(msg)

def unique_user_email(form, field):
    result = db_session.query(User).filter_by(email=field.data).first()
    print('Email ')
    if result is not None and form.self_edit_email.data != form.email.data:
        msg = field.data+' ya tiene una cuenta asociada.'
        raise ValidationError(msg)

def unique_tool_name(form, field):
    result = db_session.query(Tool).filter_by(name=field.data).first()
    if result is not None and form.self_edit.data != form.name.data:
        msg = field.data+' ya existe.'
        raise ValidationError(msg)

def is_image(message=u'¡Solo imágenes!'):
    extensions = ('jpg', 'jpeg', 'png', 'gif')
    def _is_image(form, field):
        if not field.data:
            return _is_image
        if field.data.content_type.split('/')[0] != 'image':
            raise ValidationError(message)
    return _is_image

def date_is_older(form, field):
    if form.start_date.data > form.end_date.data: #bigger means older
        msg = u'La fecha de finalización debe ser posterior a la de inicio.'
        raise ValidationError(msg)

class ExtendedRegisterForm(RegisterForm):
    first_name = StringField('Nombre', [Required()])
    last_name = StringField('Apellidos', [Required()])
    telegram = StringField('Telegram', [validators.Optional(), validators.Regexp('[a-zA-Z0-9_-]{5,}', message=u'Introduzca un usuario válido de Telegram sin @')])
    year = SelectField('Curso', [Required()], choices=[('1', 'Primero'), ('2', 'Segundo'), ('3', 'Tercero'), ('4', 'Cuarto')])
    school = SelectField('Escuela', choices=json_choices_centros('./static/json/centros.json'), id='select_school', default=59)
    degree = SelectField('Plan de Estudios', choices=json_choices_planes('./static/json/planes.json'), id='select_degree', default='59EC')
    dni = StringField('DNI o NIE', validators=[unique_user_dni,validators.Regexp('[0-9A-Z][0-9]{7}[A-Z]', message=u'Introduzca un DNI o NIE válido en mayúsculas.'), Required()])
    self_edit = HiddenField()

class EditMemberForm(Form):
    first_name = StringField('Nombre', [Required()])
    last_name = StringField('Apellidos', [Required()])
    email = StringField('Email', [unique_user_email,Required()])
    telegram = StringField('Telegram', [validators.Optional(), validators.Regexp('[a-zA-Z0-9_-]{5,}', message=u'Introduzca un usuario válido de Telegram sin @')])
    year = SelectField('Curso', [Required()], choices=[('1', 'Primero'), ('2', 'Segundo'), ('3', 'Tercero'), ('4', 'Cuarto')])
    school = SelectField('Escuela', choices=json_choices_centros('./static/json/centros.json'), id='select_school', default=59)
    degree = SelectField('Plan de Estudios', choices=json_choices_planes('./static/json/planes.json'), id='select_degree', default='59EC')
    dni = StringField('DNI o NIE', validators=[unique_user_dni,validators.Regexp('[0-9A-Z][0-9]{7}[A-Z]', message=u'Introduzca un DNI o NIE válido en mayúsculas.'), Required()])
    self_edit_dni = HiddenField()
    self_edit_email = HiddenField()
    submit = SubmitField('Guardar')

class EmailForm(Form):
    subject = StringField('Asunto', [Required()])
    message = TextAreaField('Mensaje', [Required()])
    attachment = FileField('Adjunto')

class ToolForm(Form):
    self_edit = HiddenField()
    name = StringField('Nombre',  validators=[unique_tool_name,Required()])
    description = TextAreaField('Descripcion')
    location = StringField('Lugar', [Required()])
    manual = StringField('Manual')
    documentation = StringField(u'Documentación')
    image = FileField(u'Fotografía', [is_image(u'Solo se permiten subir imágenes')])
    maintainer = SelectField('Maintainer', choices=choices_users(), id='select_maintainer', validators=[Required()])

class WorkshopForm(Form):
    name = StringField('Nombre',  validators=[Required()])
    description = TextAreaField(u'Descripción')
    location = StringField('Lugar', [Required()])
    instructor = SelectField('Instructor', choices=choices_users(), id='select_instructor', validators=[Required()])
    date = DateField('Fecha', validators=[Required()], default=date.today(), format='%Y-%m-%d')
    participants = IntegerField('Participantes')
    tooling = SelectField('Habilita',coerce=int, choices=choices_tools(), id='select_tool', default=0)
    members_only = BooleanField('Solo miembros')
    image = FileField(u'Fotografía', [is_image(u'Solo se permiten subir imágenes')])

class VotingForm(Form):
    name = StringField(u'Nombre',  validators=[Required()])
    description = TextAreaField(u'Descripción')
    start_date = DateField(u'Fecha de inicio', validators=[Required()], default=date.today(), format='%Y-%m-%d')
    end_date = DateField(u'Fecha de finalización', validators=[date_is_older,Required()], default=date.today() + timedelta(days=1), format='%Y-%m-%d')
    options = TextAreaField(u'Opciones',  validators=[Required()])

class VoteForm(Form):
    option = RadioField(u'Opción', id='select_instructor')

