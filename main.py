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

  usernames = [ item[0] for item in command.execute("SELECT Username FROM Players").fetchall() ]  # the command returns an array of tuples, which is unhelpful here as each tuple has one element
  if username in usernames:
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


def verify_college(collid, collpass):
  con = sqlite3.connect(DB_PATH)
  curs = con.cursor()
  command = "SELECT CollegePassword FROM Colleges WHERE CollegeID=?"
  password = curs.execute(command, [collid]).fetchone()[0]
  con.close()
  if not password:
    return False
  return bcrypt.checkpw(collpass.encode("utf-8"), password)


def verify_student(username, userpassword):
  con = sqlite3.connect(DB_PATH)
  curs = con.cursor()
  command = "SELECT Password FROM Players WHERE Username=?"
  password = curs.execute(command, [username]).fetchone()[0]
  con.close()
  if not password:
    return False
  return bcrypt.checkpw(userpassword.encode("utf-8"), password)

def get_team_names_scores(leagueid):
  con = sqlite3.connect(DB_PATH)
  curs = con.cursor()
  # INNER JOINS WOOOOOOOO!!!
  # DISTINCT is needed because Bye-ins are handled by having a team play twice. This causes the command to otherwise return that team twice.
  command = "SELECT DISTINCT Teams.TeamName, FixtureLink.FixtureScore FROM FixtureLink INNER JOIN Teams ON FixtureLink.TeamID = Teams.TeamID WHERE Teams.LeagueID=? ORDER BY FixtureLink.FixtureScore ASC"
  result = curs.execute(command, [leagueid]).fetchall()
  con.close()
  return result

def get_fixtures(leagueid):
  con = sqlite3.connect(DB_PATH)
  curs = con.cursor()
  command = "SELECT TeamID from Teams WHERE LeagueID = ?"
  teams = curs.execute(command, [leagueid]).fetchall()
  
  con.close()
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
  command = "SELECT Teams.TeamName, Leagues.LeagueName, Leagues.LeagueTier FROM Teams INNER JOIN Leagues ON Teams.LeagueID = Leagues.LeagueID WHERE Teams.CollegeID=?"
  result = curs.execute(command, [collegeid]).fetchall()
  con.close()
  return result

def get_collegedetails(collegeid): 
  con = sqlite3.connect(DB_PATH)
  curs = con.cursor()
  collegedetails = curs.execute("SELECT CollegeName, CollegeContact, CollegeDiscord FROM Colleges WHERE CollegeID=?", [collegeid]).fetchone()
  con.close()
  return collegedetails

##########
# Routes #
##########
@app.route('/')
@app.route("/index.html")
def get_index():
  return flask.render_template("index.html")


@app.route('/studentsignup', methods=['GET', 'POST'])
def adduser():
  error = ""
  if flask.request.method == "POST":
    form_input = flask.request.form
    # TODO: THERE HAS TO BE A BETTER WAY OF DOING THIS
    if (form_input.get('usrname') and form_input.get('pass')
        and form_input.get('passconf') and form_input.get('name')
        and form_input.get('gtag') and form_input.get('riotid')):
      if (form_input["pass"] == form_input["passconf"]):
        # this is pretty cluttered but the old version was hard to understand
        if insert_player(form_input.get('usrname'), form_input.get('pass'),
                         form_input.get('name'), form_input.get('gtag'),
                         form_input.get('riotid')): 
          return flask.render_template('adduser.html', success=True)
        else:
          error = "Username is taken"
      else:
        error = "Passwords do not match"
    else:
      error = "All fields must be filled in"
  print(error)
  return flask.render_template('adduser.html', error=error)


@app.route("/colleges")
def show_colleges():
  # TODO EXTRAS: display teams
  if flask.request.args.get("collegeid"):
    details = get_collegedetails(flask.request.args.get("collegeid"))
    if not details:
       return "<h1>400 Not a valid CollegeID</h1>", 400

    return flask.render_template("teams.html", collegeinfo=details, teams=get_college_teams(flask.request.args.get("collegeid")))
  else:
    return flask.render_template("colleges.html", tabledata=loaddata("Colleges", "CollegeID", "CollegeName"))


@app.route("/leagues")
def show_leagues():
  if flask.request.args.get("leagueid"): # so apparently request.form is only for POST method
    # TODO: Add list of fixtures, the participating team, the date, EXTRAS: has it happened yet (see if scores are placed yet)
    leaguename = get_leaguename(flask.request.args.get("leagueid"))
    if not leaguename:
      return "<h1>400 Not a valid LeagueID</h1>", 400
    print(get_fixtures(flask.request.args.get("leagueid")))
    return flask.render_template("fixture.html",leaguename=leaguename[0], leagueleaderboard=get_team_names_scores(flask.request.args.get("leagueid")))
  else:
    return flask.render_template("leagues.html", tabledata=loaddata("Leagues", "LeagueID", "LeagueName"))


@app.route('/collegelogin', methods=['GET', 'POST'])
def college_login():
  collid = flask.request.cookies.get('collID')
  if collid:
    return flask.redirect("/collegemanage")
  error = ""
  if flask.request.method == "POST":
    form_input = flask.request.form
    if form_input.get("collid") and form_input.get("pass") and form_input.get("collid").isdigit():
      if verify_college(form_input.get("collid"), form_input.get("pass")):
        resp = flask.make_response(flask.redirect("/collegemanage"))
        resp.set_cookie("collID", bytes(form_input.get("collid"), "utf8"))
        return resp
      else:
        error = "CollegeID or Password not correct"
    else:
      error = "All fields must be filled in. CollegeID must be a number."
  print(error)
  return flask.render_template("collegelogin.html", error=error)


@app.route('/studentlogin', methods=['GET', 'POST'])
def student_login():
  userid = flask.request.cookies.get('playerID')
  if userid:
    return flask.redirect("/studentmanage")
  error = ""
  if flask.request.method == "POST":
    form_input = flask.request.form
    if form_input.get("username") and form_input.get("pass"):
      if verify_student(form_input.get("username"), form_input.get("pass")):
        resp = flask.make_response(flask.redirect("/studentmanage"))
        resp.set_cookie("playerID", bytes(form_input.get("username"), "utf8"))
        return resp
      else:
        error = "Username or Password not correct"
    else:
      error = "All fields must be filled in."
  print(error)
  return flask.render_template("studentlogin.html", error=error)


@app.route("/collegemanage")
def collegemanage():
  collid = flask.request.cookies.get('collID')
  if collid:
    return flask.render_template("collegemanage.html")
  else:
    return flask.redirect("/collegelogin")


@app.route("/studentmanage")
def studentmanage():
  userid = flask.request.cookies.get('playerID')
  if userid:
    return flask.render_template("studentmanage.html")
  else:
    return flask.redirect("/studentlogin")


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
    if flask.request.method == "POST":
      form_input = flask.request.form
      if form_input.get('usrname') and form_input.get('teamid'):
        add_team_player(form_input.get('usrname'), form_input.get('teamid'))
        return flask.render_template("jointeam.html", tabledata=loaddata("Teams", "TeamID", "TeamName"), success=True, username=userid)
      else:
        error = "All fields must be filled in"
    return flask.render_template("jointeam.html", tabledata=loaddata("Teams", "TeamID", "TeamName"), error=error, username=userid)
  else:
    return flask.redirect("/studentlogin")

# i get these too much, so might as well make it entertaining
@app.errorhandler(500)
def internal_crisis(e):
  return flask.render_template('500.html', error=e), 500


#############
# Main Loop #
#############
if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080)

# The End