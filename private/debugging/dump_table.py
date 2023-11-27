#!/usr/bin/env python3
import sqlite3
from sys import argv

DB_PATH = "../heel.db"
con = sqlite3.connect(DB_PATH)
command = con.cursor()
if len(argv) == 2:
  if argv[1] == "all":
    # this gets all the table names in the database through a meta table, excluding all the other meta tables
    tables = command.execute("SELECT name FROM sqlite_schema WHERE type ='table' AND name NOT LIKE 'sqlite_%';").fetchall() 
    for i in tables:
      print(i[0] + ":")
      for j in command.execute("SELECT * FROM " + i[0]).fetchall():
        print("", j)
      
    con.close()
  else:
    command.execute("SELECT * FROM " + argv[1])
    for i in command.fetchall():
      print(i)
    con.close()
else:
  print(argv[0], "table_to_view")