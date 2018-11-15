import os
import sqlite3
import pandas as pd

data_url = 'https://people.sc.fsu.edu/~jburkardt/data/csv/addresses.csv'
headers = ['first_name','last_name','address','city','state','zip']
data_table = pd.read_csv(data_url, header=None, names=headers, converters={'zip': str})
members_db = 'aetel_members.db'

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

# Clear example.db if it exists
if os.path.exists(members_db):
    #os.remove('example.db')
    print("Found database")
    conn = create_connection(members_db)
else:
    conn = create_connection(members_db)
    # Add the data to our database
    data_table.to_sql('data_table', conn, dtype={
        'first_name':'VARCHAR(256)',
        'last_name':'VARCHAR(256)',
        'address':'VARCHAR(256)',
        'city':'VARCHAR(256)',
        'state':'VARCHAR(2)',
        'zip':'VARCHAR(5)',
    })

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
