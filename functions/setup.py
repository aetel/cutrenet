import os
import sqlite3
from passlib.hash import sha256_crypt

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def create_admin():
    email = 'admin@example.com'
    dni = '00000001A'
    password = sha256_crypt.encrypt(str('admin'))
    cur = conn.cursor()
    try:
        cur.execute("INSERT OR IGNORE INTO "+data_table+" (email,dni,password) VALUES (?,?,?) ", (email,dni,password) )
    except sqlite3.IntegrityError:
        print('ERROR: ID already exists in PRIMARY KEY column {}'.format(id_column))
    conn.commit()

database = 'aetel_members.db'
data_table = 'data_table'

sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS projects (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    begin_date text,
                                    end_date text
                                ); """

sql_create_tasks_table = """CREATE TABLE IF NOT EXISTS tasks (
                                id integer PRIMARY KEY,
                                name text NOT NULL,
                                priority integer,
                                status_id integer NOT NULL,
                                project_id integer NOT NULL,
                                begin_date text NOT NULL,
                                end_date text NOT NULL,
                                FOREIGN KEY (project_id) REFERENCES projects (id)
                            );"""

sql_create_members_table = """CREATE TABLE IF NOT EXISTS data_table (
                                dni VARCHAR(256) PRIMARY KEY,
                                first_name VARCHAR(256),
                                last_name VARCHAR(256),
                                email VARCHAR(256),
                                school VARCHAR(256),
                                degree VARCHAR(256),
                                year INTEGER,
                                telegram VARCHAR(256),
                                password VARCHAR(256),
                                begin_date VARCHAR(256),
                                end_date VARCHAR(256),
                                CONSTRAINT email UNIQUE (email)
                            );"""

# create a database connection
conn = sqlite3.connect(database)

if conn is not None:
    # create projects table
    #create_table(conn, sql_create_projects_table)
    # create tasks table
    #create_table(conn, sql_create_tasks_table)

    create_table(conn, sql_create_members_table)
else:
    print("Error! cannot create the database connection.")

create_admin()
conn.close()
