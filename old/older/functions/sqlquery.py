#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sqlite3

database = 'aetel_members.db'

# Make a convenience function for running SQL queries
def sql_query(query):
    #conn = sqlite3.connect(database)
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    #conn.close()
    return rows

def sql_query_passwd(query,var):
    #conn = sqlite3.connect(database)
    cur = conn.cursor()
    conn.text_factory = str
    cur.execute(query,var)
    passwd = cur.fetchone()
    #conn.close()
    return passwd

def sql_edit_insert(query,var):
    #conn = sqlite3.connect(database)
    cur = conn.cursor()
    cur.execute(query,var)
    conn.commit()
    #conn.close()

def sql_delete(query,var):
    #conn = sqlite3.connect(database)
    cur = conn.cursor()
    cur.execute(query,var)
    #conn.close()

def sql_query2(query,var):
    #conn = sqlite3.connect(database)
    cur = conn.cursor()
    cur.execute(query,var)
    rows = cur.fetchall()
    #conn.close()
    return rows

#This prints the lines in the database page
conn = sqlite3.connect(database)
conn.row_factory = sqlite3.Row
