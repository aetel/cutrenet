#!/usr/bin/env python
# -*- coding: utf-8 -*-
from models import User, Role
from database import db_session, init_db
from flask_security import SQLAlchemySessionUserDatastore
import os

def setup_db():
    if not os.path.exists('./aetel.db'):
        print('Creating database...')
        user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)
        init_db()

        print('Creating admin role...')
        admin_role = user_datastore.find_or_create_role(name='admin', description='Administrator')
        member_role = user_datastore.find_or_create_role(name='member', description='Miembro Activo')
        db_session.commit()

        print('Adding admin to database...')
        user_datastore.create_user(email='admin@example.com',
                             password='admin', dni='00000001A',
                             year=99, degree='AA', school='00',
                             first_name='Michael Ignatius',
                             last_name='Thomas Malloc',
                             telegram="aetelbot", roles=[admin_role,member_role])
        db_session.commit()

        print('Database created.')
    else:
        print('Database already exists.')


setup_db()