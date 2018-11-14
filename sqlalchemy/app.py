from flask import Flask
from flask_security import Security, login_required, \
     SQLAlchemySessionUserDatastore
from database import db_session, init_db
from models import User, Role

# Create app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['SECURITY_PASSWORD_SALT'] = '/2aX16zPnnIgfMwkOjGX4S'


# Setup Flask-Security
user_datastore = SQLAlchemySessionUserDatastore(db_session,
                                                User, Role)
security = Security(app, user_datastore)

# Create a user to test with
@app.before_first_request
def create_user():
    init_db()
    user_datastore.create_user(email='admin@example.com', password='admin')
    db_session.commit()

# Views
@app.route('/')
@login_required
def home():
    return 'Here you go!'

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    flash(u'Deslogueado satisfactoriamente', 'normal')
    return redirect('login', code=302)

if __name__ == '__main__':
    app.run()