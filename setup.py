#!/usr/bin/env python
# -*- coding: utf-8 -*-
from models import User, Role, Tool, Workshop, Voting, Option
from database import db_session, init_db
from flask_security import SQLAlchemySessionUserDatastore
import os
from datetime import datetime, timedelta


def setup_fake_data():
    print('Adding fake data to database...')

    tool = Tool(name=u'Martillo', description=u'Pa martillar', location=u'AETEL – Panel de herramientas', manual=u'here', documentation=u'there')
    db_session.add(tool)

    workshop1 = Workshop(name=u'Croquetas Caseras', description=u'¿Alguna vez has querido hacer tus propias croquetas caseras?', \
                        members_only=False, participants=99, date=(datetime.now() + timedelta(days=1)))
    db_session.add(workshop1)

    workshop2 = Workshop(name=u'Empanadillas Caseras', description=u'¿Alguna vez has querido hacer tus propias empanadillas caseras?', \
                        members_only=True, participants=99, date=datetime.now())
    db_session.add(workshop2)

    test_user = db_session.query(User).filter_by(dni='00000001A').first()

    test_user.workshop_instructor.append(workshop1)
    test_user.workshop_instructor.append(workshop2)

    tool.workshops.append(workshop1)
    test_user.tool_maintainer.append(tool)
    
    db_session.commit()

    nombre = u'¡Elegimos fiesta nacional!'
    voting = Voting(name=nombre, description='Fiesta fiesta fiesta', \
                    start_date=datetime.now(), end_date=(datetime.now() + timedelta(days=3)) )
    db_session.add(voting)
    db_session.commit()

    option1 = Option(name=u'Día Nacional de la croqueta', voting_id = db_session.query(Voting).filter_by(name=nombre).first().id )
    db_session.add(option1)
    option2 = Option(name=u'Día Nacional de la empanadilla', voting_id = db_session.query(Voting).filter_by(name=nombre).first().id )
    db_session.add(option2)

    db_session.commit()

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

        user_datastore.create_user(email='kek@kek.kek',
                         password='kekkek', dni='00000002A',
                         year=99, degree='AA', school='00',
                         first_name='kek',
                         last_name='kek',
                         telegram="kekkek", roles=['member'])
        db_session.commit()
        
        setup_fake_data()

        print('Database created.')
    else:
        print('Database already exists.')


setup_db()