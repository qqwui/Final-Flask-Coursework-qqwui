#!/usr/bin/env python3
import sqlite3
from os import path, remove

#######################################################################################
# !! DO USE THIS CODE IN PRODUCTION !!                                                #
# PASSWORDS ARE NOW HASHED yippee                                                     #
# IF YOU DO USE THIS, PLEASE ADD A PASSWORD HASHING ALGORITHM SUCH AS BCRYPT did that #
# AND PUT THE PASSWORDS ON A SEPERATE FILE lmao no                                    #
#######################################################################################

DB_PATH = "../heel.db"

def create_db():
  conn = sqlite3.connect(DB_PATH)
  curs = conn.cursor()
  curs.execute("""
  CREATE TABLE "Colleges" (
	"CollegeID"	TEXT,
  "CollegePassword" BLOB,
	"CollegeName"	TEXT,
	"CollegeContact"	TEXT,
	"CollegeDiscord"	TEXT,
	PRIMARY KEY("CollegeID")
  )
  """)
  curs.execute("""
  CREATE TABLE "Leagues" (
	"LeagueID"	TEXT,
	"LeagueName"	TEXT,
	"LeagueYearCreated"	TEXT,
	"LeagueTier"	TEXT,
	PRIMARY KEY("LeagueID")
  )
  """)
  curs.execute("""
  CREATE TABLE "Fixtures" (
	"FixtureID"	TEXT,
	"FixtureDate"	TEXT,
	PRIMARY KEY("FixtureID")
  )
  """)
  curs.execute("""
  CREATE TABLE "FixtureLink" (
	"TeamID"	TEXT,
	"FixtureID"	TEXT,
	"FixtureScore"	INTEGER,
	PRIMARY KEY("TeamID","FixtureID")
  )
  """)
  curs.execute("""
  CREATE TABLE "Players" (
  "Username"  TEXT,
  "Password"  BLOB,
	"PlayerName"	TEXT,
	"GamerTag"	TEXT,
	"RiotID"	TEXT,
	PRIMARY KEY("Username")
  )
  """)
  curs.execute("""
  CREATE TABLE "PlayerLink" (
	"Username"	TEXT,
	"TeamID"	TEXT,
	PRIMARY KEY("Username","TeamID")
  )
  """)
  curs.execute("""
  CREATE TABLE "Teams" (
	"TeamID"	TEXT,
	"CollegeID"	TEXT,
	"LeagueID"	TEXT,
  "TeamName" TEXT,
	PRIMARY KEY("TeamID")
  )
  """)
  conn.commit()
  conn.close()
  print("Database created successfully")

if not path.exists(DB_PATH):
  create_db()
else:
  if input("Database exists. Delete? (y/N) ").lower() == "y":
    remove(DB_PATH)
    create_db()
  else:
    print("Canceled")