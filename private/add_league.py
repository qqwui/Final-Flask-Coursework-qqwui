#!/usr/bin/env python3
import sqlite3
from random import randint
from sys import argv

DB_PATH = "heel.db"

if len(argv) == 3:
  Leaguename, Leagueyear = argv[1:3]
else:
  Leaguename = input("Enter League name: ")
  Leagueyear = input("Enter League Year: ")

conn = sqlite3.connect(DB_PATH)
command = conn.cursor()

Leagueid = str(randint(1, 99999)).zfill(5)  # I hope there are no clashes

adddetails = "INSERT INTO Leagues (LeagueID, LeagueName, LeagueYearCreated) VALUES (?,?,?)"
print([Leagueid, Leaguename, Leagueyear])
command.execute(adddetails, [Leagueid, Leaguename, Leagueyear])
conn.commit()
conn.close()
