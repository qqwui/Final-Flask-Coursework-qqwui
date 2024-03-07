# Once upon a time...
import flask
import sqlite3
import bcrypt
import random

#############
# Constants #
#############
DB_PATH = "private/heel.db"

###########
# Globals #
###########
app = flask.Flask('app')


###########
# Helpers #
###########
def loaddata(table, *attributes):
  # this is a VERY insecure way of doing this
  # never EVER *EVER* insert user input into this function, it's vulnerable to sql injection
  con = sqlite3.connect(DB_PATH)
  command = con.cursor()
  tosearch = ", ".join(attributes)
  data = command.execute("SELECT {} FROM {}".format(tosearch, table)).fetchall()
  con.close()
  return data


def insert_player(username, password, playername, gamertag, riotid):
  con = sqlite3.connect(DB_PATH)
  command = con.cursor()

  # if the username is taken, the statement will evalutate to true as all values not Null are truthy
  if not command.execute("SELECT Username FROM Players WHERE Username = ?", [username]).fetchone():
    con.close()
    return False

  salt = bcrypt.gensalt()
  hashedpw = bcrypt.hashpw(password.encode("utf-8"), salt)

  adddetails = "INSERT INTO Players (Username, Password, PlayerName, GamerTag, RiotID) VALUES (?,?,?,?,?)"
  command.execute(adddetails, [username, hashedpw, playername, gamertag, riotid])
  con.commit()
  con.close()
  return True


def insert_team(collid, leagueid, teamname):
  con = sqlite3.connect(DB_PATH)
  command = con.cursor()
  # Ideally there would be some code to check if the resulting string is already taken, but I'll take a gamble
  teamid = str(random.randint(1, 99999)).zfill(5)
  command.execute("INSERT INTO Teams (TeamID, CollegeID, LeagueID, TeamName) VALUES (?,?,?,?)", [teamid, collid, leagueid, teamname])
  con.commit()
  con.close()


def add_team_player(usrname, teamid):
  con = sqlite3.connect(DB_PATH)
  command = con.cursor()
  command.execute("INSERT INTO PlayerLink (Username, TeamID) VALUES (?,?)", [usrname, teamid])
  con.commit()
  con.close()

def add_fixture_scores(fixtureid, teamid, score):
  con = sqlite3.connect(DB_PATH)
  command = con.cursor()
  command.execute("UPDATE FixtureLink SET FixtureScore=? WHERE TeamID=? AND FixtureID=?", [score, teamid, fixtureid])
  con.commit()
  con.close()

def verify_college(collid, collpass):
  con = sqlite3.connect(DB_PATH)
  curs = con.cursor()
  command = "SELECT CollegePassword FROM Colleges WHERE CollegeID=?"
  password = curs.execute(command, [collid]).fetchone()
  con.close()
  # if the password is not filled, the collegeid doesnt exist
  if not password:
    return False
  return bcrypt.checkpw(collpass.encode("utf-8"), password[0])


def verify_player(username, userpassword):
  con = sqlite3.connect(DB_PATH)
  curs = con.cursor()
  command = "SELECT Password FROM Players WHERE Username=?"
  password = curs.execute(command, [username]).fetchone()
  con.close()
  if not password:
    return False
  return bcrypt.checkpw(userpassword.encode("utf-8"), password[0])

def get_team_names_scores(leagueid):
  con = sqlite3.connect(DB_PATH)
  curs = con.cursor()
  # INNER JOINS WOOOOOOOO!!!
  command = "SELECT Teams.TeamName, FixtureLink.FixtureScore FROM FixtureLink INNER JOIN Teams ON FixtureLink.TeamID = Teams.TeamID WHERE Teams.LeagueID=?"
  teamscores = curs.execute(command, [leagueid]).fetchall()
  con.close()

  teams = set(x[0] for x in teamscores) # get unique teams
  result = []
  for team in teams:
    totalscore = sum([fixture[1] for fixture in teamscores if fixture[0] == team])
    result.append((team, totalscore))
  result.sort(key=lambda a: a[1], reverse=True)
  
  return result

def get_leaguename(leagueid): 
  # A lot of these get_x() functions have the same simple SELECT queries.
  # However, I cant make a general function like loaddata() as userdata is inputted into these functions
  con = sqlite3.connect(DB_PATH)
  curs = con.cursor()
  leaguename = curs.execute("SELECT LeagueName FROM Leagues WHERE LeagueID=?", [leagueid]).fetchone()
  con.close()
  return leaguename

def get_college_teams(collegeid):
  con = sqlite3.connect(DB_PATH)
  curs = con.cursor()
  # I think I'm going insane with INNER JOINS. At least I'm more confident with Paper 2 SQL.
  command = "SELECT Teams.TeamName, Leagues.LeagueName FROM Teams INNER JOIN Leagues ON Teams.LeagueID = Leagues.LeagueID WHERE Teams.CollegeID=?"
  result = curs.execute(command, [collegeid]).fetchall()
  con.close()
  return result

def get_collegedetails(collegeid): 
  con = sqlite3.connect(DB_PATH)
  curs = con.cursor()
  collegedetails = curs.execute("SELECT CollegeName, CollegeContact, CollegeDiscord FROM Colleges WHERE CollegeID=?", [collegeid]).fetchone()
  con.close()
  return collegedetails

def get_fixtures(leagueid):
  con = sqlite3.connect(DB_PATH)
  curs = con.cursor()
  result = []
  # you have no idea how long it took me to think of the following
  # The first statement gets each fixture whose FixtureLinks have TeamIDs that are in the league
  # DISTINCT: there are many FixtureLinks to one Fixture, so this will return multiple fixtures
  # the DISTINCT gets rid of results with duplicate FixtureIDs
  command = "SELECT DISTINCT Fixtures.FixtureID, Fixtures.FixtureDate, Fixtures.FixtureStreamLink FROM Fixtures INNER JOIN FixtureLink ON Fixtures.FixtureID = FixtureLink.FixtureID INNER JOIN Teams ON FixtureLink.TeamID = Teams.TeamID WHERE Teams.LeagueID = ?"
  fixtures = curs.execute(command, [leagueid]).fetchall()
  # Now, loop through each Fixture to find the FixtureLinks associated with it
  for fixture in fixtures:
    command = "SELECT Teams.TeamName, FixtureLink.FixtureScore From Fixtures INNER JOIN FixtureLink ON Fixtures.FixtureID = FixtureLink.FixtureID INNER JOIN Teams ON FixtureLink.TeamID = Teams.TeamID WHERE Fixtures.FixtureID = ?"
    teams = curs.execute(command, [fixture[0]]).fetchall()
    # Package them all into one neat list using some ungodly concatenation
    result.append(teams + [fixture[1], fixture[2]])

  return result

def get_college_fixtures(collegeid):
  # Most of the get_x_fixtures() functions will have the same format, its the best solution I can think of
  con = sqlite3.connect(DB_PATH)
  curs = con.cursor()
  result = []
  command = "SELECT DISTINCT Fixtures.FixtureID, Fixtures.FixtureDate FROM Fixtures INNER JOIN FixtureLink ON Fixtures.FixtureID = FixtureLink.FixtureID INNER JOIN Teams ON FixtureLink.TeamID = Teams.TeamID WHERE Teams.CollegeID = ?"
  fixtures = curs.execute(command, [collegeid]).fetchall()
  for fixture in fixtures:
    command = "SELECT Teams.TeamName From Fixtures INNER JOIN FixtureLink ON Fixtures.FixtureID = FixtureLink.FixtureID INNER JOIN Teams ON FixtureLink.TeamID = Teams.TeamID WHERE Fixtures.FixtureID = ?"
    teams = curs.execute(command, [fixture[0]]).fetchall()
    command = "SELECT Teams.TeamID FROM Fixtures INNER JOIN FixtureLink ON Fixtures.FixtureID = FixtureLink.FixtureID INNER JOIN Teams ON FixtureLink.TeamID = Teams.TeamID WHERE Fixtures.FixtureID = ? AND Teams.CollegeID = ?"
    college_teamid = curs.execute(command, [fixture[0], collegeid]).fetchone()
    result.append(teams + [fixture[0], college_teamid[0]])

  con.close()
  return result

def get_player_team(username):
  con = sqlite3.connect(DB_PATH)
  curs = con.cursor()
  # again, .fetchone() returns a single tuple with only one element, which messes up get_upcoming_team_fixtures()
  team = curs.execute("SELECT Teams.TeamID FROM PlayerLink INNER JOIN Teams ON PlayerLink.TeamID = Teams.TeamID WHERE PlayerLink.Username = ?", [username]).fetchone()
  con.close()
  # team[0]: get the first and only element, needs to make sure team exists before i can use subscript to get the first element
  return team[0] if team else False

def get_upcoming_team_fixtures(teamid):
  con = sqlite3.connect(DB_PATH)
  curs = con.cursor()
  result = []
  # Fixtures.FixtureDate >= strftime('%F'): fixture dates are stored in YYYY-MM-DD form i.e. ISO 8601, strftime('%F') gives the current date in YYYY-MM-DD form so it can be compared
  # Its kinda cool this can be done despite sqlite storing dates as strings
  # Fixtures.FixtureDate IS NULL: or the fixture date is empty i.e. date not settled yet, ideally in the future
  # Also, I just learnt that you can put brackets around WHERE statements to have them evaluated first
  command = "SELECT DISTINCT Fixtures.FixtureID, Fixtures.FixtureDate FROM Fixtures INNER JOIN FixtureLink ON Fixtures.FixtureID = FixtureLink.FixtureID WHERE (Fixtures.FixtureDate >= strftime('%F') OR Fixtures.FixtureDate IS NULL) AND FixtureLink.TeamID = ?"
  fixtures = curs.execute(command, [teamid]).fetchall()
  for fixture in fixtures:
    command = "SELECT Teams.TeamName, FixtureLink.FixtureScore From Fixtures INNER JOIN FixtureLink ON Fixtures.FixtureID = FixtureLink.FixtureID INNER JOIN Teams ON FixtureLink.TeamID = Teams.TeamID WHERE Fixtures.FixtureID = ?"
    teams = curs.execute(command, [fixture[0]]).fetchall()
    result.append(teams + [fixture[1]])

  con.close()
  return result

##########
# Routes #
##########
@app.route('/')
@app.route("/index.html")
def get_index():
  return flask.render_template("index.html")


@app.route('/playersignup', methods=['GET', 'POST'])
def adduser():
  error = ""
  if flask.request.method == "POST":
    form_input = flask.request.form
    # TODO: THERE HAS TO BE A BETTER WAY OF DOING THIS
    if (form_input.get('usrname') and form_input.get('pass')
        and form_input.get('passconf') and form_input.get('name')
        and form_input.get('gtag') and form_input.get('riotid')):
      if (form_input["pass"] == form_input["passconf"]):
        # this is pretty cluttered but the old version was hard to see what arguments it needed
        if insert_player(form_input.get('usrname'), form_input.get('pass'),
                         form_input.get('name'), form_input.get('gtag'),
                         form_input.get('riotid')): 
          resp = flask.make_response(flask.redirect("/playerdashboard"))
          resp.set_cookie("playerID", form_input.get("username"))
          return resp
        else:
          error = "Username is taken"
      else:
        error = "Passwords do not match"
    else:
      error = "All fields must be filled in"
  return flask.render_template('adduser.html', error=error)


@app.route("/colleges")
def show_colleges():
  # if flask.request.args.get("collegeid"): display college details if we have the collegeid in the url, otherwise, display a list of colleges
  if flask.request.args.get("collegeid"):
    details = get_collegedetails(flask.request.args.get("collegeid"))
    # failsafe in case invalid leagueid is used
    if not details:
      # if you add a number to the end of a return for an app route, it will use that number as the http status code
      # 400 is just a generic "you didnt format your request correctly", which i guess is technically true
      return "<h1>400 Not a valid CollegeID</h1>", 400

    return flask.render_template("teams.html", collegeinfo=details, teams=get_college_teams(flask.request.args.get("collegeid")))
  else:
    return flask.render_template("colleges.html", tabledata=loaddata("Colleges", "CollegeID", "CollegeName"))


@app.route("/leagues")
def show_leagues():
  if flask.request.args.get("leagueid"): # so apparently request.form is only for POST method
    leaguename = get_leaguename(flask.request.args.get("leagueid"))
    if not leaguename:
      return "<h1>400 Not a valid LeagueID</h1>", 400
    return flask.render_template("fixture.html",leaguename=leaguename[0], leagueleaderboard=get_team_names_scores(flask.request.args.get("leagueid")), fixtures=get_fixtures(flask.request.args.get("leagueid")))
  else:
    return flask.render_template("leagues.html", tabledata=loaddata("Leagues", "LeagueID", "LeagueName"))


@app.route('/collegelogin', methods=['GET', 'POST'])
def college_login():
  # http cookies are cool, i dont have to use javascript to access them
  collid = flask.request.cookies.get('collID')
  if collid:
    return flask.redirect("/collegemanage")
  error = ""
  if flask.request.method == "POST":
    form_input = flask.request.form
    if form_input.get("collid") and form_input.get("pass") and form_input.get("collid").isdigit():
      if verify_college(form_input.get("collid"), form_input.get("pass")):
        # the day i learnt you could set cookies and redirect at the same time saved so much code
        resp = flask.make_response(flask.redirect("/collegemanage"))
        resp.set_cookie("collID", form_input.get("collid"))
        return resp
      else:
        error = "CollegeID or Password not correct"
    else:
      error = "All fields must be filled in. CollegeID must be a number."

  return flask.render_template("collegelogin.html", error=error)

@app.route("/signout")
def signout():
  # the code is about the same for both colleges and players, so might as well kill two birds with one stone
  resp = flask.make_response(flask.redirect("/index.html"))
  resp.set_cookie("collID", "", expires=0) # this just sets the cookie data to null and the expire date to 1970-01-01, hopefully in the past
  resp.set_cookie("playerID", "", expires=0)
  return resp

@app.route('/playerlogin', methods=['GET', 'POST'])
def player_login():
  userid = flask.request.cookies.get('playerID')
  if userid:
    return flask.redirect("/playerdashboard")
  error = ""
  if flask.request.method == "POST":
    form_input = flask.request.form
    if form_input.get("username") and form_input.get("pass"):
      if verify_player(form_input.get("username"), form_input.get("pass")):
        resp = flask.make_response(flask.redirect("/playerdashboard"))
        resp.set_cookie("playerID", form_input.get("username"))
        return resp
      else:
        error = "Username or Password not correct"
    else:
      error = "All fields must be filled in."
  return flask.render_template("playerlogin.html", error=error)

@app.route("/collegemanage")
def collegemanage():
  collid = flask.request.cookies.get('collID')
  if collid:
    # get_collegedetails(collid)[0]: pretty cool trick i thought of to just get the name of the college without creating a whole new function
    return flask.render_template("collegemanage.html", college_name=get_collegedetails(collid)[0])
  else:
    return flask.redirect("/collegelogin")

@app.route("/playerdashboard")
def playermanage():
  userid = flask.request.cookies.get('playerID')
  if userid:
    teamid = get_player_team(userid)
    if teamid:
      return flask.render_template("playerdashboard.html", fixtures=get_upcoming_team_fixtures(teamid))
    else:
      return flask.render_template("playermanage.html")
  else:
    return flask.redirect("/playerlogin")


@app.route("/createteam", methods=['GET', 'POST'])
def createteam():
  collid = flask.request.cookies.get('collID')
  if collid:
    error = ""
    if flask.request.method == "POST":
      form_input = flask.request.form
      if form_input.get('teamname') and form_input.get('league') and form_input.get('collid'):
        insert_team(form_input.get("collid"), form_input.get('league'), form_input.get('teamname'))
        return flask.render_template("createteam.html", tabledata=loaddata("Leagues", "LeagueID", "LeagueName", "LeagueYearCreated"), success=True, collid=collid)
      else:
        error = "All fields must be filled in"
    return flask.render_template("createteam.html", tabledata=loaddata("Leagues", "LeagueID", "LeagueName", "LeagueYearCreated"), error=error, collid=collid)
  else:
    return flask.redirect("/collegelogin")


@app.route("/jointeam", methods=['GET', 'POST'])
def jointeam():
  userid = flask.request.cookies.get('playerID')
  if userid:
    error = ""
    if get_player_team(userid):
      return flask.redirect("/playerdashboard")
    if flask.request.method == "POST":
      form_input = flask.request.form
      if form_input.get('usrname') and form_input.get('teamid'):
        add_team_player(form_input.get('usrname'), form_input.get('teamid'))
        return flask.redirect("/playerdashboard")
      else:
        error = "All fields must be filled in"
    return flask.render_template("jointeam.html", tabledata=loaddata("Teams", "TeamID", "TeamName"), error=error, username=userid)
  else:
    return flask.redirect("/playerlogin")
  
@app.route("/fixturemanage", methods=['GET', 'POST'])
def fixturemanage():
  collid = flask.request.cookies.get('collID')
  if collid:
    error=""
    if flask.request.method == "POST":
      form_input = flask.request.form
      if form_input.get('score') and form_input.get("fixture"):
        # I DID IT. I PUT A TRY EXCEPT CLAUSE IN THE CODE, ARE YOU HAPPY NOW?
        try:
          score = int(form_input.get('score'))
          fixtureid, teamid = form_input.get("fixture").split(" ")
          add_fixture_scores(fixtureid, teamid, score)
        except ValueError:
          error = "Score must be a number"
      else:
        error = "All fields must be filled in"
    return flask.render_template("fixturemanage.html", tabledata=get_college_fixtures(collid), error=error)
  else:
    return flask.redirect("/collegelogin")

# i get these too much, so might as well make it entertaining
@app.errorhandler(500)
def internal_crisis(e):
  return flask.render_template('500.html', error=e), 500


#############
# Main Loop #
#############
if __name__ == "__main__":
  app.run(host='127.0.0.1', port=8080)

# The End