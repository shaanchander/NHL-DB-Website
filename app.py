from pickle import NONE
from flask import Flask, flash, redirect, render_template, request, session
from functions import *

TEAMS_SHORT = ["ANA", "ARI", "BOS", "BUF", "CGY", "CAR", "CHI", "COL", "CBJ", "DAL", "DET", "EDM", "FLA", "LAK", "MIN", "MTL", "NSH", "NJD", "NYI", "NYR", "OTT", "PHI", "PIT", "SJS", "SEA", "STL", "TBL", "TOR", "VAN", "VGK", "WSH", "WIN"]
TEAMS_LONG = ["Anaheim Ducks", "Arizona Coyotes", "Boston Bruins", "Buffalo Sabres", "Calgary Flames", "Carolina Hurricanes", "Chicago Blackhawks", "Colorado Avalanche", "Columbus Blue Jackets", "Dallas Stars", "Detroit Red Wings", "Edmonton Oilers", "Florida Panthers", "Los Angeles Kings", "Minnesota Wild", "Montreal Canadiens", "Nashville Predators", "New Jersey Devils", "New York Islanders", "New York Rangers", "Ottawa Senators", "Philadelphia Flyers", "Pittsburgh Penguins", "San Jose Sharks", "Seattle Kraken", "St Louis Blues", "Tampa Bay Lightning", "Toronto Maple Leafs", "Vancouver Canucks", "Vegas Golden Knights", "Washington Capitals", "Winnipeg Jets"]
# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/playerSearch", methods = ['GET', 'POST'])
def player_Search():

    curSeason = "20212022"

    if request.method == "GET":
        # print("current season: {}".format(CURRENT_SEASON))
        return render_template("playerSearch.html", TEAMS_SHORT = TEAMS_SHORT, TEAMS_LONG = TEAMS_LONG)

    # gets info from form
    fName = request.form.get("fName")
    lName = request.form.get("lName")
    # season = request.form.get("season")
    team = request.form.get('team')

    # gets player id
    if team == '0':
        id = playerSearch(fName, lName)
    else:
        # team = team.upper()
        id = playerSearch(fName, lName, team)

    # error traps if player isn't in NHL API db
    if id == 0:
        return render_template("error.html", message = "Player Not Found")

    # gets career stats
    stats = allPlayerStats(id)

    # gets personal info
    pInfo = peopleInfo(id)

    # if pInfo['birthStateProvince'] == "":
    #     pInfo['birthInfo'] = f"{pInfo['birthCity']}, {pInfo['birthCountry']}"
    # else:
    #     pInfo['birthInfo'] = f"{pInfo['birthCity']}, {pInfo['birthStateProvince']}, {pInfo['birthCountry']}"

    # if their profile has no birth province/state or does
    try:
        pInfo['birthInfo'] = f"{pInfo['birthCity']}, {pInfo['birthStateProvince']}, {pInfo['birthCountry']}"
    except:
         pInfo['birthInfo'] = f"{pInfo['birthCity']}, {pInfo['birthCountry']}"

    # creates link for player image
    link = f"http://nhl.bamcontent.com/images/headshots/current/168x168/{id}.jpg"

    return render_template("playerInfo.html", info = stats, person = pInfo, imgLink = link)

@app.route("/teamSearch", methods = ['GET', 'POST'])
def team_Search():

    if request.method == "GET":
        return render_template("teamSearch.html", TEAMS_SHORT = TEAMS_SHORT, TEAMS_LONG = TEAMS_LONG)

    team = request.form.get("team")

    if team not in TEAMS_SHORT:
        return render_template("error.html", message = "Team Not Found")

    # gets team info
    team_info = teamInfo(team)
    team_roster = teamRoster(team)

    # get each player's stats

    return render_template("teamInfo.html", teamInfo = team_info, teamRoster = team_roster)





@app.route("/schedule")
def schedule():
    if request.method == "GET":
        return render_template("schedule.html")