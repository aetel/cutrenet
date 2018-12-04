#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_security.forms import Form, RegisterForm, StringField, Required, validators
from wtforms import SelectField, TextField, TextAreaField, FileField, ValidationError
from database import db_session
from models import User
import json

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

def unique_user_dni(form, field):
    result = db_session.query(User).filter_by(dni=field.data).first()
    if result is not None:
        msg = field.data+' ya tiene una cuenta asociada.'
        raise ValidationError(msg)

class ExtendedRegisterForm(RegisterForm):
    first_name = StringField('First Name', [Required()])
    last_name = StringField('Last Name', [Required()])
    telegram = StringField('Telegram', [validators.Optional(), validators.Regexp('[a-zA-Z0-9_-]{5,}', message="Introduzca un usuario valido de Telegram sin @")])
    year = SelectField('Curso', [Required()], choices=[('1', 'Primero'), ('2', 'Segundo'), ('3', 'Tercero'), ('4', 'Cuarto')])
    school = SelectField('Escuela', choices=json_choices_centros('./static/json/centros.json'), id='select_school', default=59)
    degree = SelectField('Plan de Estudios', choices=json_choices_planes('./static/json/planes.json'), id='select_degree', default='59EC')
    dni = StringField('DNI o NIE', validators=[unique_user_dni,validators.Regexp('[0-9A-Z][0-9]{7}[A-Z]', message="Introduzca un DNI o NIE valido"), Required()])

class EmailForm(Form):
    subject = TextField('Asunto', [Required()])
    message = TextAreaField('Mensaje', [Required()])
    attachment = FileField('Adjunto')

class ToolForm(Form):
    name = TextField('Nombre', [Required()])
    description = TextAreaField('Descripcion', [Required()])
    location = TextField('Lugar', [Required()])
    manual = TextField('Manual', [Required()])
    documentation = TextField('Documentacion', [Required()])

