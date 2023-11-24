#!/usr/bin/env python3
import sqlite3

DB_PATH = "/home/runner/Final-Flask-Coursework-qqwui/private/heel.db"

user_response = input("(D) to modify fixture dates or (S) to add fixture scores: ").upper()

con = sqlite3.connect(DB_PATH)
curs = con.cursor()

if user_response == "D":
  # again, INNER JOIN in INNER JOIN *just* to get team names
  # i'll probs just copy paste the command from main.py into here
  pass
elif user_response == "S":
  pass
else:
  print("not a valid choice, canceling")

con.close()