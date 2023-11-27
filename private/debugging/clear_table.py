#!/usr/bin/env python3
import sqlite3
from sys import argv

DB_PATH = "../heel.db"
con = sqlite3.connect(DB_PATH)
command = con.cursor()

if len(argv) == 2:
  tables = [ table[0] for table in command.execute("SELECT name FROM sqlite_schema WHERE type ='table' AND name NOT LIKE 'sqlite_%';").fetchall() ]
  if argv[1] in tables:
    print(command.execute("SELECT * FROM " + argv[1]).fetchall())
    if input("Are you sure you want to delete " + argv[1] + ": ").lower() == "y":
      command.execute("DELETE FROM " + argv[1])
      con.commit()
      print("Deleted all entries of " + argv[1])
    else:
      print("Canceled")
  else:
    print("Not a valid table")
  con.close()
else:
  print(argv[0], "table_to_delete")