#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, flash, redirect, render_template, request, session, abort, Response
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from passlib.hash import argon2
import os
import sqlite3

app = Flask(__name__)

#config
app.config.update(
    DEBUG = True,
    SECRET_KEY = os.urandom(16),
    host='127.0.0.1',
    port=4000
)
#Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' #the login view of our application

# silly user model
class User(UserMixin):
    # proxy for a database of users
    user_database = {"JohnDoe": ("JohnDoe", "John"),
               "JaneDoe": ("JaneDoe", "Jane")}

    def __init__(self, id, username, pw_hash):
        self.id = id
        self.name = username
        self.pw_hash = pw_hash

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)

    @classmethod
    def get(cls,id):
        return cls.user_database.get(id)

# callback to reload the user object
@login_manager.user_loader
def load_user(dni):
    from functions.sqlquery import sql_query, sql_query2, sql_query_fone
    print('dni: '+str(dni))
    name = sql_query_fone("SELECT first_name FROM data_table WHERE dni = ?", (dni,))
    pw_hash = sql_query_fone("SELECT password FROM data_table WHERE dni = ?", (dni,))
    print('name: '+str(name[0])+' pw_hash: '+pw_hash[0])
    return User(dni,name,pw_hash)

@app.route('/')
@login_required
def home():
    from functions.sqlquery import sql_query
    results = sql_query(''' SELECT * FROM data_table''')
    msg = 'SELECT * FROM data_table'
    return render_template('database.html', results=results, msg=msg)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            from functions.sqlquery import sql_query, sql_query2, sql_query_fone
            error = None
            POST_USERNAME = str(request.form['email'])
            POST_PASSWORD = str(request.form['password'])
            print("Username: "+POST_USERNAME+"\nPassword: "+POST_PASSWORD)
            query = sql_query_fone("SELECT password FROM data_table WHERE email = ?", (POST_USERNAME,))
            if query is not None:
                for pw_hash in query:
                    if argon2.verify(POST_PASSWORD, pw_hash):
                        dni = sql_query_fone("SELECT dni FROM data_table WHERE email = ?", (POST_USERNAME,))
                        print(dni[0])
                        user = User(dni[0],POST_USERNAME,pw_hash)
                        login_user(user)
                    else:
                        error = 'Invalid password'
                        flash(u'Contraseña incorrecta', 'error')
            else:
                error = 'Invalid username'
                flash(u'El email proporcionado no coincide con el de ningún usuario', 'error')
            return redirect(request.args.get("next","/"))
        else:
            return redirect('/', code=302)
    else:
        return render_template('login.html')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    flash(u'Deslogueado satisfactoriamente', 'normal')
    return redirect('login', code=302)


# this is when user submits an insert
@app.route('/register', methods=['POST', 'GET'])
def sql_newdatainsert():
    from functions.sqlquery import sql_edit_insert, sql_query
    if request.method == 'POST':
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        email = request.form['email']
        dni = request.form['dni']
        school = request.form['school']
        degree = request.form['degree']
        year = request.form['year']
        telegram = request.form['telegram']
        password = None
        try:
            sql_edit_insert(''' INSERT INTO data_table (first_name,last_name,email,dni,school,degree,year,telegram,password) VALUES (?,?,?,?,?,?,?,?,?) ''',
                            (first_name, last_name, email, dni, school, degree, year, telegram, password))
            flash(u'Registrado correctamente', 'success')
            results = sql_query(''' SELECT * FROM data_table''')
            msg = 'INSERT INTO data_table (first_name,last_name,email,dni,school,degree,year) VALUES (' + first_name + \
                ',' + last_name + ',' + email + ',' + dni + ',' + school + \
                ',' + degree + ',' + year + ',' + telegram + ')'
            return render_template('register.html', results=results, msg=msg)
        except sqlite3.Error as er:
            if 'dni' in er.message:
                flash(u'DNI ya registrado', 'error')
                return render_template('register.html', p_last_name=last_name, p_first_name=first_name, p_email=email, p_school=school, p_degree=degree, p_year=year, p_telegram=telegram)
            elif 'email' in er.message:
                flash(u'Email ya registrado', 'error')
                return render_template('register.html', p_last_name=last_name, p_first_name=first_name, p_dni=dni, p_school=school, p_degree=degree, p_year=year, p_telegram=telegram)
            else:
                print('SOMETHING ELSE')
                flash(u'Database Error')
                # log this
                return render_template('register.html', p_last_name=last_name, p_first_name=first_name, p_email=email, p_dni=dni, p_school=school, p_degree=degree, p_year=year, p_telegram=telegram)
    else:
        return render_template('register.html')


# this is when user submits an insert
@app.route('/insert', methods=['POST', 'GET'])
@login_required
def sql_datainsert():
    from functions.sqlquery import sql_edit_insert, sql_query
    if request.method == 'POST':
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        email = request.form['email']
        dni = request.form['dni']
        school = request.form['school']
        degree = request.form['degree']
        year = request.form['year']
        telegram = request.form['telegram']
        password = argon2.hash(str(request.form['password']))
        sql_edit_insert(''' INSERT INTO data_table (first_name,last_name,email,dni,school,degree,year,telegram,password) VALUES (?,?,?,?,?,?,?,?,?) ''',
                        (first_name, last_name, email, dni, school, degree, year, telegram, password))
    results = sql_query(''' SELECT * FROM data_table''')
    msg = 'INSERT INTO data_table (first_name,last_name,email,dni,school,degree,year,password) VALUES (' + first_name + ',' + \
        last_name + ',' + email + ',' + dni + ',' + school + ',' + \
        degree + ',' + year + ',' + telegram + ',' + password + ')'
    return render_template('database.html', results=results, msg=msg)


# this is when user clicks delete link
@app.route('/delete', methods=['POST', 'GET'])
@login_required
def sql_datadelete():
    from functions.sqlquery import sql_delete, sql_query
    if request.method == 'GET':
        dni = request.args.get('dni')
        sql_delete(''' DELETE FROM data_table where dni = ?''', (dni,))
        flash(u'Borrado satisfactoriamente', 'success')
    results = sql_query(''' SELECT * FROM data_table''')
    msg = 'DELETE FROM data_table WHERE dni = ' + dni
    return render_template('database.html', results=results, msg=msg)


# this is when user clicks edit link
@app.route('/query_edit', methods=['POST', 'GET'])
@login_required
def sql_editlink():
    from functions.sqlquery import sql_query, sql_query2
    if request.method == 'GET':
        edni = request.args.get('edni')
        eresults = sql_query2(
            ''' SELECT * FROM data_table where dni = ? ''', (edni,))
    results = sql_query(''' SELECT * FROM data_table''')
    return render_template('database.html', eresults=eresults, results=results)


# this is when user submits an edit
@app.route('/edit', methods=['POST', 'GET'])
@login_required
def sql_dataedit():
    from functions.sqlquery import sql_edit_insert, sql_query
    if request.method == 'POST':
        old_dni = request.form['old_dni']
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        email = request.form['email']
        dni = request.form['dni']
        school = request.form['school']
        degree = request.form['degree']
        year = request.form['year']
        telegram = request.form['telegram']
        password = request.form['password']
        if password == '':
            pw_hash = None
        else:
            pw_hash = argon2.hash(str(request.form['password']))
        sql_edit_insert(''' UPDATE data_table set first_name=?,last_name=?,email=?,dni=?,school=?,degree=?,year=?,telegram=?,password=? WHERE dni=? ''',
                        (first_name, last_name, email, dni, school, degree, year, telegram, pw_hash, old_dni))
        flash(u'Editado satisfactoriamente', 'success')
    results = sql_query(''' SELECT * FROM data_table''')
    msg = 'UPDATE data_table set first_name = ' + first_name + ', last_name = ' + last_name + ', email = ' + email + ', dni = ' + dni + ', school = ' + \
        school + ', degree = ' + degree + ', year = ' + year + ', telegram = ' + \
        telegram + ', password = ' + \
        str(pw_hash) + ' WHERE dni = ' + old_dni
    return render_template('database.html', results=results, msg=msg)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=4000)

