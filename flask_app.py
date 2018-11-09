#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, flash, redirect, render_template, request, session, abort
from passlib.hash import argon2
import os
import sqlite3

app = Flask(__name__)


@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        from functions.sqlquery import sql_query
        results = sql_query(''' SELECT * FROM data_table''')
        msg = 'SELECT * FROM data_table'
        return render_template('database.html', results=results, msg=msg)


@app.route('/login', methods=['POST', 'GET'])
def do_admin_login():
    if request.method == 'POST':
        if not session.get('logged_in'):
            from functions.sqlquery import sql_query, sql_query2, sql_query_passwd
            error = None
            POST_USERNAME = str(request.form['email'])
            POST_PASSWORD = str(request.form['password'])
            print("Username: "+POST_USERNAME+"\n Password: "+POST_PASSWORD)
            query = sql_query_passwd(
                "SELECT password FROM data_table WHERE email = ?", (POST_USERNAME,))
            if query is not None:
                for pw_hash in query:
                    if argon2.verify(POST_PASSWORD, pw_hash):
                        session['logged_in'] = True
                        session['user'] = POST_USERNAME
                    else:
                        error = 'Invalid password'
                        flash(u'Contraseña incorrecta', 'error')
            else:
                error = 'Invalid username'
                flash(u'El email proporcionado no coincide con el de ningún usuario', 'error')
            return redirect('/', code=302)
        else:
            return redirect('/', code=302)
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    session['logged_in'] = False
    return home()


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
def sql_datainsert():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
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
def sql_datadelete():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
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
def sql_editlink():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        from functions.sqlquery import sql_query, sql_query2
        if request.method == 'GET':
            edni = request.args.get('edni')
            eresults = sql_query2(
                ''' SELECT * FROM data_table where dni = ? ''', (edni,))
        results = sql_query(''' SELECT * FROM data_table''')
        return render_template('database.html', eresults=eresults, results=results)


# this is when user submits an edit
@app.route('/edit', methods=['POST', 'GET'])
def sql_dataedit():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
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
    app.secret_key = os.urandom(12)
    app.run(debug=True, host='127.0.0.1', port=4000)
