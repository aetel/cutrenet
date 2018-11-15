from flask_security.forms import RegisterForm, StringField, Required, validators
from wtforms import SelectField

class ExtendedRegisterForm(RegisterForm):
    first_name = StringField('First Name', [Required()])
    last_name = StringField('Last Name', [Required()])
    telegram = StringField('Telegram Username', [Required()])
    year = StringField('Curso', [Required()])
    year = SelectField(u'Curso', [Required()], choices=[('1', 'Primero'), ('2', 'Segundo'), ('3', 'Tercero'), ('4', 'Cuarto')])
    school = StringField('Escuela', [Required()])
    degree = StringField('Plan de Estudios', [Required()])
    dni = StringField('DNI o NIE', [validators.Regexp('[0-9A-Z][0-9]{7}[A-Z]', message="Introduzca un DNI o NIE valido"), Required()])
