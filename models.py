from database import Base
from flask_security import UserMixin, RoleMixin
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Boolean, DateTime, Date, Column, Integer, \
                       String, ForeignKey

class RolesUsers(Base):
    __tablename__ = 'roles_users'
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(), ForeignKey('user.id'))
    role_id = Column('role_id', Integer(), ForeignKey('role.id'))

class Role(Base, RoleMixin):
    __tablename__ = 'role'
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))

class User(Base, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    dni = Column(String(255), unique=True)
    password = Column(String(255))
    school = Column(String(255))
    degree = Column(String(255))
    year = Column(Integer)
    telegram = Column(String(255))
    last_login_at = Column(DateTime())
    current_login_at = Column(DateTime())
    last_login_ip = Column(String(100))
    current_login_ip = Column(String(100))
    login_count = Column(Integer)
    active = Column(Boolean())
    email_confirmed_at = Column(DateTime())
    member_since = Column(DateTime())
    roles = relationship('Role', secondary='roles_users',
                         backref=backref('users', lazy='dynamic'))
    tools = relationship('Tool', secondary='workshops_users',
                         backref=backref('users', lazy='dynamic'))
class VotesUsers(Base):
    __tablename__ = 'votes_users'
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(), ForeignKey('user.id'))
    option_id = Column('option_id', Integer(), ForeignKey('option.id'))

class Option(Base):
    __tablename__ = 'option'
    id = Column(Integer(), primary_key=True)
    vote_id = Column('vote_id', Integer(), ForeignKey('vote.id'))
    name = Column(String(80), unique=True)
    votes = relationship('Vote', secondary='votes_users',
                         backref=backref('users', lazy='dynamic'))
class Vote(Base):
    __tablename__ = 'vote'
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))
    start_date = Column(Date())
    end_date = Column(Date())
    options = relationship('Option', secondary='option',
                     backref=backref('votes', lazy='dynamic'))

class WorkshopsUsers(Base):
    __tablename__ = 'workshops_users'
    id = Column(Integer(), primary_key=True)
    workshop_id = Column('workshop_id', Integer(), ForeignKey('workshop.id'))
    user_id = Column('user_id', Integer(), ForeignKey('user.id'))
    paid = Column(Boolean())
    complete = Column(Boolean())

class Workshop(Base):
    __tablename__ = 'workshop'
    id = Column(Integer(), primary_key=True)
    name = Column(String(80))
    description = Column(String(255))
    instructor = Column('instructor', Integer(), ForeignKey('user.id'))
    members_only = Column(Boolean())
    participants = Column(Integer)
    tools = relationship('Tool', secondary='tools_workshops',
                     backref=backref('workshops', lazy='dynamic'))

class ToolsWorkshops(Base):
    __tablename__ = 'tools_workshops'
    id = Column(Integer(), primary_key=True)
    tool_id = Column('tool_id', Integer(), ForeignKey('tool.id'))
    workshop_id = Column('workshop_id', Integer(), ForeignKey('workshop.id'))

class Tool(Base):
    __tablename__ = 'tool'
    id = Column(Integer(), primary_key=True)
    name = Column(String(80))
    description = Column(String(255))
    location = Column(String(100))
    manual = Column(String(100))
    documentation = Column(String(100))
