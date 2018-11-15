from flask_security.forms import RegisterForm, StringField, Required, validators
from wtforms import SelectField
import json

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

class ExtendedRegisterForm(RegisterForm):
    first_name = StringField('First Name', [Required()])
    last_name = StringField('Last Name', [Required()])
    telegram = StringField('Telegram Nick', [validators.Regexp('^[^@]+$', message="Introduzca su usuario sin @")])
    year = SelectField('Curso', [Required()], choices=[('1', 'Primero'), ('2', 'Segundo'), ('3', 'Tercero'), ('4', 'Cuarto')])
    school = SelectField('Escuela', choices=json_choices_centros('./static/json/centros.json'), id='select_school', default=59)
    degree = SelectField('Plan de Estudios', choices=json_choices_planes('./static/json/planes.json'), id='select_degree', default='59EC')
    dni = StringField('DNI o NIE', [validators.Regexp('[0-9A-Z][0-9]{7}[A-Z]', message="Introduzca un DNI o NIE valido"), Required()])
