#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from models import User, Role
from flask_security import SQLAlchemySessionUserDatastore

engine = create_engine('sqlite:///aetel.db', \
                       convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import models
    Base.metadata.create_all(bind=engine)

user_datastore = SQLAlchemySessionUserDatastore(db_session,
                                                User, Role)
init_db()
user_datastore.create_role(name='admin')
user_datastore.create_user(username='admin', email='admin@example.com',
                         password='admin', roles=['admin'])
db_session.commit()