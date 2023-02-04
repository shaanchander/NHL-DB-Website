from pickle import NONE
from flask import Flask, flash, redirect, render_template, request, session
from functions import *

TEAMS_SHORT = ["ANA", "ARI", "BOS", "BUF", "CGY", "CAR", "CHI", "COL", "CBJ", "DAL", "DET", "EDM", "FLA", "LAK", "MIN", "MTL", "NSH", "NJD", "NYI", "NYR", "OTT", "PHI", "PIT", "SJS", "SEA", "STL", "TBL", "TOR", "VAN", "VGK", "WSH", "WIN"]
TEAMS_LONG = ["Anaheim Ducks", "Arizona Coyotes", "Boston Bruins", "Buffalo Sabres", "Calgary Flames", "Carolina Hurricanes", "Chicago Blackhawks", "Colorado Avalanche", "Columbus Blue Jackets", "Dallas Stars", "Detroit Red Wings", "Edmonton Oilers", "Florida Panthers", "Los Angeles Kings", "Minnesota Wild", "Montréal Canadiens", "Nashville Predators", "New Jersey Devils", "New York Islanders", "New York Rangers", "Ottawa Senators", "Philadelphia Flyers", "Pittsburgh Penguins", "San Jose Sharks", "Seattle Kraken", "St. Louis Blues", "Tampa Bay Lightning", "Toronto Maple Leafs", "Vancouver Canucks", "Vegas Golden Knights", "Washington Capitals", "Winnipeg Jets"]

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/playerSearch", methods = ['GET', 'POST'])
def player_Search():

    curSeason = CURRENT_SEASON

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
    team_stats = teamStats(team)
    

    # get each player's stats

    return render_template("teamInfo.html", teamInfo = team_info, teamRoster = team_roster, teamStats = team_stats)


@app.route("/scheduleSearch", methods = ['GET', 'POST'])
def schedule():
    if request.method == "GET":
        return render_template("scheduleSearch.html", TEAMS_SHORT = TEAMS_SHORT, TEAMS_LONG = TEAMS_LONG, timeZones = pytz.common_timezones_set)

    team = request.form.get("team")
    matchup = request.form.get("matchup")
    tz = request.form.get("tz")

    # return render_template("error.html", message = len(matchup))

    team_schedule = teamSchedule(team, tz)

    if matchup != '0':
        for i in range(len(team_schedule)):

            teams = [team_schedule[i]['awayTeamName'], team_schedule[i]['homeTeamName']]
            targetTeams = [team, matchup]

            # return render_template("error.html", message = f"{team} - {matchup} -- {team_schedule[i]['awayTeamName']} - {team_schedule[i]['homeTeamName']}")

            if set(teams) != set(targetTeams):
                team_schedule[i]['gameStatus'] = 0
                # pass

    team_info = teamInfo(team)

    return render_template("scheduleInfo.html", teamInfo = team_info, teamSchedule = team_schedule)


@app.route("/standings", methods = ['GET'])
def standings():

    temp_standings_data = getStandings()

    #divisionSortedStandings = [{} for _ in range(TEAMS_IN_LEAGUE)]
    #conferenceSortedStandings = list([{} for _ in range(TEAMS_IN_LEAGUE)])

    east = list([{} for _ in range(TEAMS_IN_CONFERENCE[0])])
    west = list([{} for _ in range(TEAMS_IN_CONFERENCE[1])])

    atlantic = list([{} for _ in range(TEAMS_IN_DIV[0])])
    metro = list([{} for _ in range(TEAMS_IN_DIV[1])])
    central = list([{} for _ in range(TEAMS_IN_DIV[2])])
    pacific = list([{} for _ in range(TEAMS_IN_DIV[3])])

    leagueSortedStandings = [{} for _ in range(TEAMS_IN_LEAGUE)]

    # sorts standings over whole league
    for i in range(1, TEAMS_IN_LEAGUE + 1):
        for j in range(TEAMS_IN_LEAGUE):
            if int(temp_standings_data[j]['leagueRank']) == int(i):
                leagueSortedStandings[i - 1] = temp_standings_data[j]
                break

    # sorts standings over conference
    # does the east
    for k in range(TEAMS_IN_CONFERENCE[0]):
        for m in range(TEAMS_IN_LEAGUE):
            if int(temp_standings_data[m]['conferenceRank']) == int(k + 1) and temp_standings_data[m]['conferenceName'] == "Eastern":
                east[k] = temp_standings_data[m]
                break

    # does the west
    for n in range(TEAMS_IN_CONFERENCE[1]):
        for p in range(TEAMS_IN_LEAGUE):
            if int(temp_standings_data[p]['conferenceRank']) == int(n + 1) and temp_standings_data[p]['conferenceName'] == "Western":
                west[n] = temp_standings_data[p]
                break
        
    conferenceSortedStandings = [east, west]

    # sorts standings by division
    # does atlantic
    for q in range(TEAMS_IN_DIV[0]):
        for r in range(TEAMS_IN_LEAGUE):
            if int(temp_standings_data[r]['divisionRank']) == int(q + 1) and temp_standings_data[r]['divisionName'] == "Atlantic":
                atlantic[q] = temp_standings_data[r]
                break

    # does metro
    for q in range(TEAMS_IN_DIV[1]):
        for r in range(TEAMS_IN_LEAGUE):
            if int(temp_standings_data[r]['divisionRank']) == int(q + 1) and temp_standings_data[r]['divisionName'] == "Metropolitan":
                metro[q] = temp_standings_data[r]
                break

    # does the central
    for q in range(TEAMS_IN_DIV[2]):
        for r in range(TEAMS_IN_LEAGUE):
            if int(temp_standings_data[r]['divisionRank']) == int(q + 1) and temp_standings_data[r]['divisionName'] == "Central":
                central[q] = temp_standings_data[r]
                break

    # does the pacific
    for q in range(TEAMS_IN_DIV[3]):
        for r in range(TEAMS_IN_LEAGUE):
            if int(temp_standings_data[r]['divisionRank']) == int(q + 1) and temp_standings_data[r]['divisionName'] == "Pacific":
                pacific[q] = temp_standings_data[r]
                break


    divisionSortedStandings = [atlantic, metro, central, pacific]

    return render_template("standings.html", leagueStandings = leagueSortedStandings, conferenceStandings = conferenceSortedStandings, divisionStandings = divisionSortedStandings)