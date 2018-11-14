from flask_security.forms import RegisterForm, StringField, Required

class ExtendedRegisterForm(RegisterForm):
    first_name = StringField('First Name', [Required()])
    last_name = StringField('Last Name', [Required()])
    telegram = StringField('Telegram Username', [Required()])
    year = StringField('Curso', [Required()])
    school = StringField('Escuela', [Required()])
    degree = StringField('Plan de Estudios', [Required()])
    dni = StringField('DNI o NIE', [Required()])
