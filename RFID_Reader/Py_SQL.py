
"""
Created on Wed Jun 19 14:05:18 2019

@author: veberhar
"""

import pyodbc


#LINKED, RFID, SN, Desc1, 
def run_query(search):
    print("Running query")
    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=?'
                          'Database=?;'
                          'Trusted_Connection=yes;'
                          'UID=?;'
                          'PWD=%s;')
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM )" % (search))
    return cursor
