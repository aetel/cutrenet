import os
import sqlite3
import pandas as pd

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
 
    return None

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

database = 'aetel_members.db'

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
                                year VARCHAR(256),
                                telegram VARCHAR(256),
                                name VARCHAR(256),
                                begin_date VARCHAR(256),
                                end_date VARCHAR(256)
                            );"""

# create a database connection
conn = create_connection(database)
if conn is not None:
    # create projects table
    #create_table(conn, sql_create_projects_table)
    # create tasks table
    #create_table(conn, sql_create_tasks_table)

    create_table(conn, sql_create_members_table)
else:
    print("Error! cannot create the database connection.")

conn.row_factory = sqlite3.Row

# Make a convenience function for running SQL queries
def sql_query(query):
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    return rows

def sql_edit_insert(query,var):
    cur = conn.cursor()
    cur.execute(query,var)
    conn.commit()

def sql_delete(query,var):
    cur = conn.cursor()
    cur.execute(query,var)

def sql_query2(query,var):
    cur = conn.cursor()
    cur.execute(query,var)
    rows = cur.fetchall()
    return rows
