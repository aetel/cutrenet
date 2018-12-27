from database import Base
from flask_security import UserMixin, RoleMixin
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Boolean, DateTime, Date, Column, Integer, \
                       Float, String, ForeignKey

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
    money = Column(Float)
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
    # tools = relationship('Workshop', secondary='workshops_users',
    #                      backref=backref('users', lazy='dynamic'),
    #                      cascade="all, delete, delete-orphan",
    #                      single_parent=True)
    workshop_instructor = relationship('Workshop', backref='instructor', lazy=True,
                            cascade="all, delete, delete-orphan",
                            single_parent=True)
    tool_maintainer = relationship('Tool', backref='maintainer', lazy=True,
                            cascade="all, delete, delete-orphan",
                            single_parent=True)
    _workshops = relationship('Workshop', secondary='workshops_users', backref=backref('workshops_users_backref', lazy='dynamic'))

class VotesUsers(Base):
    __tablename__ = 'votes_users'
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(), ForeignKey('user.id'))
    option_id = Column('option_id', Integer(), ForeignKey('option.id'))

class Option(Base):
    __tablename__ = 'option'
    id = Column(Integer, primary_key=True)
    name = Column(String(280))
    description = Column(String(255))
    voting_id = Column(Integer, ForeignKey("voting.id"))
    votings = relationship("Voting", back_populates="options",
                            cascade="all, delete, delete-orphan",
                            single_parent=True)
    votes = relationship("User", backref=backref('votes', lazy='dynamic'),
                    cascade="all, delete",
                    secondary='votes_users')

class Voting(Base):
    __tablename__ = 'voting'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))
    start_date = Column(Date())
    end_date = Column(Date())
    options = relationship("Option", back_populates="votings",
                            cascade="all, delete, delete-orphan")

class WorkshopsUsers(Base):
    __tablename__ = 'workshops_users'
    id = Column(Integer(), primary_key=True)
    workshop_id = Column('workshop_id', Integer(), ForeignKey('workshop.id'))
    user_id = Column('user_id', Integer(), ForeignKey('user.id'))
    paid = Column(Boolean())
    complete = Column(Boolean())

class Tool(Base):
    __tablename__ = 'tool'
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))
    location = Column(String(100))
    manual = Column(String(100))
    documentation = Column(String(100))
    image = Column(String(80))
    maintainer_id = Column('maintainer', Integer(), ForeignKey('user.id'))
    workshops = relationship('Workshop', backref='tool', lazy=True,
                            cascade="all, delete, delete-orphan",
                            single_parent=True)

class Workshop(Base):
    __tablename__ = 'workshop'
    id = Column(Integer(), primary_key=True)
    name = Column(String(80))
    description = Column(String(255))
    location = Column(String(80))
    instructor_id = Column('instructor', Integer(), ForeignKey('user.id'))
    date = Column(Date())
    members_only = Column(Boolean())
    participants = Column(Integer)
    image = Column(String(80))
    tool_id = Column('tooling', Integer(), ForeignKey('tool.id'))
    users = relationship('User', backref='workshops',
                    secondary='workshops_users')
