#!/usr/bin/env python3
import sqlite3
import re
from sys import argv

DB_PATH = "heel.db"

def print_fixtureids(leagueid):
  con = sqlite3.connect(DB_PATH)
  curs = con.cursor()

  result = []
  command = "SELECT DISTINCT Fixtures.FixtureID FROM Fixtures INNER JOIN FixtureLink ON Fixtures.FixtureID = FixtureLink.FixtureID INNER JOIN Teams ON FixtureLink.TeamID = Teams.TeamID WHERE Teams.LeagueID = ?"
  fixtures = curs.execute(command, [leagueid]).fetchall()
  for i in fixtures:
    command = "SELECT Teams.TeamName, FixtureLink.FixtureScore From Fixtures INNER JOIN FixtureLink ON Fixtures.FixtureID = FixtureLink.FixtureID INNER JOIN Teams ON FixtureLink.TeamID = Teams.TeamID WHERE Fixtures.FixtureID = ?"
    teams = curs.execute(command, [i[0]]).fetchall()
    result.append([i[0]] + teams)

  for row in result:
    print(row)
  
  con.close()

def update_fixture_details(fixtureid, fixturedate, fixturestreamlink):
  con = sqlite3.connect(DB_PATH)
  curs = con.cursor()

  if fixturedate:
    if fixturestreamlink:
      command = "UPDATE Fixtures SET FixtureDate=?, FixtureStreamLink=? WHERE FixtureID=?"
      curs.execute(command, [fixturedate, fixturestreamlink, fixtureid])
    else:
      command = "UPDATE Fixtures SET FixtureDate=? WHERE FixtureID=?"
      curs.execute(command, [fixturedate, fixtureid])
  else:
    command = "UPDATE Fixtures SET FixtureStreamLink=? WHERE FixtureID=?"
    curs.execute(command, [fixturestreamlink, fixtureid])

  con.commit()
  con.close()


leagueid = input("Enter LeagueID to get fixtures for: ")

print_fixtureids(leagueid)

fixtureid = input("Enter FixtureID to enter details for: ")
fixturedate = input("Enter date for fixture in YYYY-MM-DD (or leave blank to keep): ")
fixturestreamlink = input("Enter Stream Link for fixture (or leave blank to keep): ")

if fixturedate:
  if re.search("(\d{4})-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])", fixturedate):
    update_fixture_details(fixtureid, fixturedate, fixturestreamlink)
    print("Details updated")
  else:
    print("Invalid Date format")
