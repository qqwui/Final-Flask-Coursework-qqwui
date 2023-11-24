#!/usr/bin/env python3
import sqlite3
import random
from sys import argv

DB_PATH = "/home/runner/Final-Flask-Coursework-qqwui/private/heel.db"

def get_teams(leagueid):
  con = sqlite3.connect(DB_PATH)
  curs = con.cursor()
  teams = curs.execute("SELECT TeamID, TeamName FROM Teams WHERE LeagueID=?", [leagueid]).fetchall()

  con.close()
  return teams

def add_fixtures(fixtures):
  con = sqlite3.connect(DB_PATH)
  curs = con.cursor()
  for i in fixtures:
    fixtureid = str(random.randint(1, 99999)).zfill(5)
    curs.execute('INSERT INTO Fixtures (FixtureID) VALUES (?)', [fixtureid])

    curs.execute('INSERT INTO FixtureLink (TeamID, FixtureID, FixtureScore) VALUES (?, ?, 0)', [i[0][0], fixtureid])
    curs.execute('INSERT INTO FixtureLink (TeamID, FixtureID, FixtureScore) VALUES (?, ?, 0)', [i[1][0], fixtureid])

  con.commit()
  con.close()

def create_fixtures_sheet(fixtures, filename):
  towrite = ""
  for i in fixtures:
    towrite += "{0} ({1}) vs. {2} ({3})\n".format(i[0][1], i[0][0], i[1][1], i[1][0])
    # towrite += i[0][1] + " (" + i[0][0] + ") vs. " + i[1][1] + " (" + i[1][0] + ")\n"
  file = open(filename, "w")
  file.write(towrite)
  file.close()

if len(argv) >= 3:
  leagueid = argv[1]
  fixuresheet = argv[2]
  
  teamsinleague = get_teams(leagueid)
  # i'm using the pop function which acts on the array itself, so i save a copy to preserve the original
  teamstopair = teamsinleague.copy()
  random.shuffle(teamstopair)
  
  fixtures = []
  
  while not len(teamstopair) <= 1:
    team_a = teamstopair.pop()
    team_b = teamstopair.pop()
    
    fixtures.append([team_a,team_b])

  if len(teamstopair) != 0:
    team_c = teamstopair.pop()
    # this is why i need to preserve the original team list
    # this just pairs the bye-in team with a random team that's not itself
    teamsinleague.remove(team_c)
    team_d = teamsinleague[random.randrange(0, len(teamsinleague))]
    fixtures.append([team_c, team_d])

  print(fixtures)
  add_fixtures(fixtures)
  create_fixtures_sheet(fixtures, argv[2])
else:
  print(argv[0], "leagueid", "sheet_file_name")