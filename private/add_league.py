#!/usr/bin/env python3
import sqlite3
from random import randint
from sys import argv

DB_PATH = "/home/runner/Final-Flask-Coursework-qqwui/private/heel.db"

if len(argv) > 1:
  Leaguename, Leagueyear, Leaguetier = argv[1:4]
else:
  Leaguename = input("Enter League name: ")
  Leagueyear = input("Enter League Year: ")
  Leaguetier = input("Enter League Tier: ")

conn = sqlite3.connect(DB_PATH)
command = conn.cursor()

Leagueid = str(randint(1, 99999)).zfill(5)  # I hope there are no clashes

adddetails = "INSERT INTO Leagues (LeagueID, LeagueName, LeagueYearCreated, LeagueTier) VALUES (?,?,?,?)"
print([Leagueid, Leaguename, Leagueyear, Leaguetier])
command.execute(adddetails, [Leagueid, Leaguename, Leagueyear, Leaguetier])
conn.commit()
conn.close()
