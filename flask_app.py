from flask import Flask, flash, redirect, render_template, request, session, abort
import sys
import os

sys.path.insert(1, "PATH TO LOCAL PYTHON PACKAGES")  #OPTIONAL: Only if need to access Python packages installed on a local (non-global) directory
sys.path.insert(2, "PATH TO FLASK DIRECTORY")      #OPTIONAL: Only if you need to add the directory of your flask app

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

@app.route('/login', methods=['POST'])
def do_admin_login():
    if not session.get('logged_in'):
        from functions.sqlquery import sql_query, sql_query2
        error = None
        POST_USERNAME = str(request.form['username'])
        POST_PASSWORD = str(request.form['password'])
        
        query = sql_query2(''' SELECT * FROM data_table where first_name = ? and last_name = ?''', (POST_USERNAME,POST_PASSWORD))
        if query:
            session['logged_in'] = True
        else:
            error = 'Invalid credentials'
            flash(u'Invalid password provided', 'error')
        return redirect('/', code=302)
    else:
        return redirect('/', code=302)

@app.route('/login')
def login():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return redirect('/', code=302)
 
@app.route('/logout')
def logout():
    session['logged_in'] = False
    return home()

@app.route('/register') #this is when user submits an insert
def register():
    return render_template('register.html')

@app.route('/registerdo',methods = ['POST', 'GET']) #this is when user submits an insert
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
        sql_edit_insert(''' INSERT INTO data_table (first_name,last_name,email,dni,school,degree,year,telegram) VALUES (?,?,?,?,?,?,?,?) ''', (first_name,last_name,email,dni,school,degree,year,telegram) )
    results = sql_query(''' SELECT * FROM data_table''')
    msg = 'INSERT INTO data_table (first_name,last_name,email,dni,school,degree,year) VALUES ('+first_name+','+last_name+','+email+','+dni+','+school+','+degree+','+year+','+telegram+')'
    flash(u'Registrado correctamente', 'success')
    return render_template('register.html', results=results, msg=msg)

@app.route('/insert',methods = ['POST', 'GET']) #this is when user submits an insert
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
        sql_edit_insert(''' INSERT INTO data_table (first_name,last_name,email,dni,school,degree,year,telegram) VALUES (?,?,?,?,?,?,?,?) ''', (first_name,last_name,email,dni,school,degree,year,telegram) )
    results = sql_query(''' SELECT * FROM data_table''')
    msg = 'INSERT INTO data_table (first_name,last_name,email,dni,school,degree,year) VALUES ('+first_name+','+last_name+','+email+','+dni+','+school+','+degree+','+year+','+telegram+')'
    return render_template('database.html', results=results, msg=msg)

@app.route('/delete',methods = ['POST', 'GET']) #this is when user clicks delete link
def sql_datadelete():
    from functions.sqlquery import sql_delete, sql_query
    if request.method == 'GET':
        lname = request.args.get('lname')
        fname = request.args.get('fname')
        sql_delete(''' DELETE FROM data_table where first_name = ? and last_name = ?''', (fname,lname) )
    results = sql_query(''' SELECT * FROM data_table''')
    msg = 'DELETE FROM data_table WHERE first_name = ' + fname + ' and last_name = ' + lname
    return render_template('database.html', results=results, msg=msg)

@app.route('/query_edit',methods = ['POST', 'GET']) #this is when user clicks edit link
def sql_editlink():
    from functions.sqlquery import sql_query, sql_query2
    if request.method == 'GET':
        elname = request.args.get('elname')
        efname = request.args.get('efname')
        eresults = sql_query2(''' SELECT * FROM data_table where first_name = ? and last_name = ?''', (efname,elname))
    results = sql_query(''' SELECT * FROM data_table''')
    return render_template('database.html', eresults=eresults, results=results)

@app.route('/edit',methods = ['POST', 'GET']) #this is when user submits an edit
def sql_dataedit():
    from functions.sqlquery import sql_edit_insert, sql_query
    if request.method == 'POST':
        old_last_name = request.form['old_last_name']
        old_first_name = request.form['old_first_name']
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        email = request.form['email']
        dni = request.form['dni']
        school = request.form['school']
        degree = request.form['degree']
        year = request.form['year']
        telegram = request.form['telegram']
        sql_edit_insert(''' UPDATE data_table set first_name=?,last_name=?,email=?,dni=?,school=?,degree=?,year=?,telegram=? WHERE first_name=? and last_name=? ''', (first_name,last_name,email,dni,school,degree,year,telegram,old_first_name,old_last_name) )
    results = sql_query(''' SELECT * FROM data_table''')
    msg = 'UPDATE data_table set first_name = ' + first_name + ', last_name = ' + last_name + ', email = ' + email + ', dni = ' + dni + ', school = ' + school + ', degree = ' + degree + ', year = ' + year + ', telegram = ' + telegram + ' WHERE first_name = ' + old_first_name + ' and last_name = ' + old_last_name
    return render_template('database.html', results=results, msg=msg)

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='127.0.0.1', port=4001)
