from flask import render_template
import requests
from datetime import datetime
import pytz

# ** ENSURE THESE CONSTANTS ARE UP TO DATE **
CURRENT_SEASON = '20222023'

# east, west
TEAMS_IN_CONFERENCE = [16, 16]

# atlantic, metro, central, pacific
TEAMS_IN_DIV = [8, 8, 8, 8]

TEAMS_IN_LEAGUE = 32

TEAM_IDS_SHORT = {"ANA":24, "ARI":53, "BOS":6, "BUF":7, "CGY":20, "CAR":12, "CHI":16, "COL":21, "CBJ":29, "DAL":25, "DET":17, "EDM":22, "FLA":13, "LAK":26, "MIN":30, "MTL":8, "NSH":18, "NJD":1, "NYI":2, "NYR":3, "OTT":9, "PHI":4, "PIT":5, "SJS":28, "SEA":55, "STL":19, "TBL":14, "TOR":10, "VAN":23, "VGK":54, "WSH":15, "WIN":52}

TEAM_IDS_LONG = {"Anaheim Ducks":24, "Arizona Coyotes":53, "Boston Bruins":6, "Buffalo Sabres":7, "Calgary Flames":20, "Carolina Hurricanes":12, "Chicago Blackhawks":16, "Colorado Avalanche":21, "Columbus Blue Jackets":29, "Dallas Stars":25, "Detroit Red Wings":17, "Edmonton Oilers":22, "Florida Panthers":13, "Los Angeles Kings":26, "Minnesota Wild":30, "Montréal Canadiens":8, "Nashville Predators":18, "New Jersey Devils":1, "New York Islanders":2, "New York Rangers":3, "Ottawa Senators":9, "Philadelphia Flyers":4, "Pittsburgh Penguins":5, "San Jose Sharks":28, "Seattle Kraken":55, "St. Louis Blues":19, "Tampa Bay Lightning":14, "Toronto Maple Leafs":10, "Vancouver Canucks":23, "Vegas Golden Knights":54, "Washington Capitals":15, "Winnipeg Jets":52}

REV_TEAM_IDS_LONG = {24: "Anaheim Ducks", 53: "Arizona Coyotes", 6: "Boston Bruins", 7: "Buffalo Sabres", 20: "Calgary Flames", 12: "Carolina Hurricanes", 16: "Chicago Blackhawks", 21: "Colarado Avalanche", 29: "Columbus Blue Jackets", 25: "Dallas Stars", 17: "Detroit Red Wings", 22: "Edmonton Oilers", 13: "Florida Panthers", 26: "Los Angeles Kings", 30: "Minnesota Wild", 8: "Montréal Canadiens", 18: "Nashville Predators", 1: "New Jersey Devils", 2: "New York Islanders", 3: "New York Rangers", 9: "Ottawa Senators", 4: "Philadelphia Flyers", 5: "Pittsbirgh Penguins", 28: "San Jose Sharks", 55: "Seattle Kraken", 19: "St. Louis Blues", 14: "Tampa Bay Lightning", 10: "Toronto Maple Leafs", 23: "Vancouver Canucks", 54: "Vegas Golden Knights", 15: "Washington Capitals", 52: "Winnipeg Jets"}

VALID_TEAM = 'ANA'

# TEAM_IDS = [1,2,3,4,5,6,7,8,9,10,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,28,29,30,52,53,54]

# takes in player info, returns id, if no player is found, returns 0
def playerSearch(fName, lName, team = '0'):

    fName = fName.lower()
    lName = lName.lower()

    url = f'https://suggest.svc.nhl.com/svc/suggest/v1/minplayers/{fName} {lName}'

    response = requests.get(url)

    if response.status_code != 200:
        return 0

    data = response.json()

    for i in range(len(data['suggestions'])):
        data['suggestions'][i] = data['suggestions'][i].split('|')

    # doesn't filter by team if one isn't provided
    if team == '0':
        for i in range(len(data['suggestions'])):
            data['suggestions'][i][11] = '0'

    # checks list of returned players, returning the ID of the one with the same fName, lName, and team (if provided) as passed into the function
    for i in range(len(data['suggestions'])):
        if data['suggestions'][i][2].lower() == fName and data['suggestions'][i][1].lower() == lName and team == data['suggestions'][i][11]:
            return data['suggestions'][i][0]

    return 0


# takes in player ID and the season (if not provided, defaults to current season), returns dict of stats
def playerStats(id, season = CURRENT_SEASON):

    url = f"https://statsapi.web.nhl.com/api/v1/people/{id}/stats?stats=statsSingleSeason&season={season}"

    response = requests.get(url)

    if response.status_code != 200:
        return 0

    data = response.json()

    playerInfo = {}

    # if they don't have an id or stats? (some kind of error trapping)
    try:
        for i in data['stats'][0]['splits'][0]['stat'].keys():
            playerInfo[i] = data['stats'][0]['splits'][0]['stat'][i]
    except IndexError:
        
        playerInfo['goals'] = "-"
        playerInfo['assists'] = "-"
        playerInfo['points'] = "-"
        playerInfo['plusMinus'] = "-"

        playerInfo['savePercentage'] = "-"
        playerInfo['goalAgainstAverage'] = "-"

        return playerInfo

    try:
        # playerInfo[i]['goalAgainstAverage'] = round(playerInfo[i]['goalAgainstAverage'], 2)
        playerInfo['goalAgainstAverage'] =  "%0.2f" % round(float(playerInfo['goalAgainstAverage']), 2)
        # playerInfo[i]['savePercentage'] =  "%0.3f" % round(playerInfo[i]['savePercentage'], 3)

        for k in ["goalAgainstAverge", "wins", "savePercentage"]:
            if k not in playerInfo.keys():
                playerInfo[k] = '-'
            elif k == "savePercentage":
                playerInfo['savePercentage'] =  "%0.3f" % round(playerInfo['savePercentage'], 3)

        if playerInfo['savePercentage'][:3] == "0.0":
            playerInfo['savePercentage'] = '-'
                
    # if they are a skater
    except KeyError:
        for k in ["games", "goals", "assists", "points", "plusMinus"]:
            if k not in playerInfo.keys():
                playerInfo[k] = '-'

    return playerInfo

def allPlayerStats(id):

    url = f"https://statsapi.web.nhl.com/api/v1/people/{id}/stats?stats=yearByYear"

    response = requests.get(url)

    if response.status_code != 200:
        return 0

    data = response.json()

    playerInfo = [{} for _ in range(len(data['stats'][0]['splits']))]

    for i in range(len(data['stats'][0]['splits'])):

        # playerInfo[i]['season'] = data['stats'][0]['splits'][i]['season']

        # formats season
        temp1 = data['stats'][0]['splits'][i]['season'][:4]
        temp2 = data['stats'][0]['splits'][i]['season'][4:]
        playerInfo[i]['season'] = f"{temp1} - {temp2}"

        # gets league and team names
        playerInfo[i]['team'] = data['stats'][0]['splits'][i]['team']['name']
        playerInfo[i]['league'] = data['stats'][0]['splits'][i]['league']['name']

        # gets all other stats
        for j in data['stats'][0]['splits'][i]['stat'].keys():
            playerInfo[i][j] = data['stats'][0]['splits'][i]['stat'][j]

        # if they are a goalie
        try:
            # playerInfo[i]['goalAgainstAverage'] = round(playerInfo[i]['goalAgainstAverage'], 2)
            playerInfo[i]['goalAgainstAverage'] =  "%0.2f" % round(playerInfo[i]['goalAgainstAverage'], 2)
            # playerInfo[i]['savePercentage'] =  "%0.3f" % round(playerInfo[i]['savePercentage'], 3)

            for k in ["goalAgainstAverge", "wins", "savePercentage"]:
                if k not in playerInfo[i].keys():
                    playerInfo[i][k] = '-'
                elif k == "savePercentage":
                    playerInfo[i]['savePercentage'] =  "%0.3f" % round(playerInfo[i]['savePercentage'], 3)

            if playerInfo[i]['savePercentage'][:3] == "0.0":
                playerInfo[i]['savePercentage'] = '-'
                    
        # if they are a skater
        except KeyError:
            for k in ["games", "goals", "assists", "points", "plusMinus"]:
                if k not in playerInfo[i].keys():
                    playerInfo[i][k] = '-'

    # fills empty stats with '-'
    for i in range(len(playerInfo)):
        for j in playerInfo[i].keys():
            if playerInfo[i][j] == "":
                playerInfo[i][j] = '-'

    return playerInfo

# gets player personal info
def peopleInfo(id):
    url = f"https://statsapi.web.nhl.com/api/v1/people/{id}"

    response = requests.get(url)

    if response.status_code != 200:
        return 0

    data = response.json()

    info = {}

    # gets 
    for i in data['people'][0].keys():
        if i not in ["currentTeam", "primaryPosition"]:
            info[i] = data['people'][0][i]

    # tries to get team information
    try:
        info['teamID'] = data['people'][0]['currentTeam']['id']
        info['teamName'] = data['people'][0]['currentTeam']['name']
    except KeyError:
        pass

    # gets position info
    info['positionName'] = data['people'][0]['primaryPosition']['name']
    info['positionType'] = data['people'][0]['primaryPosition']['type']
    info['positionAbbreviation'] = data['people'][0]['primaryPosition']['abbreviation']

    # if info['fullName'] == "Tim Stützle":
    #     info['fullName'] = "Tim 'Pentagon' Stützle"

    return info

# gets team info
def teamInfo(team):

    if team == '0':
        return render_template("error.html", message = "Team not Found (field empty)")

    if len(team) == 3:
        teamID = TEAM_IDS_SHORT[team]
    elif len(team) > 3:
        teamID = TEAM_IDS_LONG[team]

    teamUrl = f"https://statsapi.web.nhl.com/api/v1/teams/{teamID}/"

    response = requests.get(teamUrl)

    if response.status_code != 200:
        return 0

    data = response.json()

    info = {}

    info['teamName'] = data['teams'][0]['name']
    info['venueName'] = data['teams'][0]['venue']['name']
    info['teamAbbreviation'] = data['teams'][0]['abbreviation']
    info['firstYearOfPlay'] = data['teams'][0]['firstYearOfPlay']
    info['divName'] = data['teams'][0]['division']['name']
    info['divAbbreviation'] =  data['teams'][0]['division']['nameShort']
    info['conferenceName'] = data['teams'][0]['conference']['name']
    info['officialSiteUrl'] = data['teams'][0]['officialSiteUrl']
    info['logoUrl'] = f"https://www-league.nhlstatic.com/images/logos/teams-current-primary-light/{teamID}.svg"

    return info

# gets team roster info
def teamRoster(team):

    teamID = TEAM_IDS_SHORT[team]

    url = f"https://statsapi.web.nhl.com/api/v1/teams/{teamID}/roster"

    response = requests.get(url)

    if response.status_code != 200:
        return 0

    data = response.json()

    # creates list of dicts
    info = [{} for _ in range(len(data['roster']))]

    # for each roster player
    for i in range(len(data['roster'])):
        info[i]['name'] = data['roster'][i]['person']['fullName']

        # just because why not
        # if info[i]['name'] == "Tim Stützle":
        #     info[i]['name'] = "Tim 'Pentagon' Stützle"

        # gets number, if none, puts '-'
        try:
            info[i]['number'] = f"#{data['roster'][i]['jerseyNumber']}"
        except KeyError:
            info[i]['number'] = '-'

        # gets remaining info
        info[i]['id'] = data['roster'][i]['person']['id']
        info[i]['positionName'] = data['roster'][i]['position']['name']
        info[i]['positionType'] = data['roster'][i]['position']['type']
        info[i]['positionAbbreviation'] = data['roster'][i]['position']['abbreviation']

        # gets their player id
        info[i]['stats'] = playerStats(info[i]['id'])

    return info

# converts datetime object from UTC to input timezone (from stackoverflow)
def utc_to_time(naive, timezone="Europe/Istanbul"):
    return naive.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(timezone))

# gets a team's schedule (returns list of dicts with info on each game)
def teamSchedule(team, timeZone, season = CURRENT_SEASON):

    # error trapping
    if team == '0':
        return render_template("error.html", message = "Team not Found")

    # gets team ID
    teamID = TEAM_IDS_LONG[team]

    url = f"https://statsapi.web.nhl.com/api/v1/schedule?teamId={teamID}&season={season}"

    response = requests.get(url)

    if response.status_code != 200:
        return response.status_code

    data = response.json()

    # initializes list of dicts
    info = [{} for _ in range(data['totalGames'])]

    # initializes counters
    totalGamesIndex = 0
    dayIndex = 0
    gameIndex = 0

    while 1:

        # info[totalGamesIndex]['gameDate'] = data['dates'][dayIndex]['games'][gameIndex]['gameDate']

        # info[totalGamesIndex]['gameTime'] = data['dates'][dayIndex]['games'][gameIndex]['gameDate']

        dateTime = data['dates'][dayIndex]['games'][gameIndex]['gameDate']

        # print(datetime.timestamp(info[totalGamesIndex]['gameDate'], tz=None))
        # exit

        # gets time in UTC of game
        year = int(dateTime[:4])
        month = int((dateTime)[5:7]) 
        day = int(dateTime[8:10])
        hour = int(dateTime[11:13])
        minute = int(dateTime[14:16])
        # second = int(dateTime[17:19])

        # print(second)
        # exit

        # converts date and time to selected timezone
        tempDate = datetime(year, month, day, hour, minute)
        tempDate = utc_to_time(tempDate, timeZone)
        info[totalGamesIndex]['gameDate'] = tempDate.strftime("%b %d, %Y")
        info[totalGamesIndex]['gameTime'] = tempDate.strftime("%I:%M%p")

        # gets remaining game info
        info[totalGamesIndex]['gameType'] =  data['dates'][dayIndex]['games'][gameIndex]['gameType']
        info[totalGamesIndex]['venueName'] = data['dates'][dayIndex]['games'][gameIndex]['venue']['name']
        info[totalGamesIndex]['awayTeamName'] = data['dates'][dayIndex]['games'][gameIndex]['teams']['away']['team']['name']
        info[totalGamesIndex]['awayTeamId'] = data['dates'][dayIndex]['games'][gameIndex]['teams']['away']['team']['id']
        info[totalGamesIndex]['homeTeamName'] = data['dates'][dayIndex]['games'][gameIndex]['teams']['home']['team']['name']
        info[totalGamesIndex]['homeTeamId'] = data['dates'][dayIndex]['games'][gameIndex]['teams']['home']['team']['id']
        info[totalGamesIndex]['gameStatus'] = data['dates'][dayIndex]['games'][gameIndex]['status']['detailedState']

        # handles counter values 
        if gameIndex < len(data['dates'][dayIndex]['games']) - 1: 
            gameIndex += 1
        else:
            dayIndex += 1
            gameIndex = 0
        totalGamesIndex += 1

        # if all games have been stored, break
        if totalGamesIndex >= data['totalGames']:
            break

    return info

# gets standings data (including wins, losses, etc.), gets from given season, if none given, defaults to current
def getStandings(season = CURRENT_SEASON):

    # season = "20212022"

    url = f"https://statsapi.web.nhl.com/api/v1/standings?season={season}"

    response = requests.get(url)

    if response.status_code != 200:
        return response.status_code

    data = response.json()

    numTeams = 0

    # initializes list of dicts
    info = [{} for _ in range(TEAMS_IN_LEAGUE)]


    # gets info for each team in each division
    for i in range(len(data['records'])):
        for j in range(len(data['records'][i]['teamRecords'])):
            info[numTeams]['conferenceName'] = data['records'][i]['conference']['name']
            info[numTeams]['divisionName'] = data['records'][i]['division']['name']

            info[numTeams]['divisionRank'] = data['records'][i]['teamRecords'][j]['divisionRank']
            info[numTeams]['conferenceRank'] = data['records'][i]['teamRecords'][j]['conferenceRank']
            info[numTeams]['leagueRank'] = data['records'][i]['teamRecords'][j]['leagueRank']

            info[numTeams]['wins'] = data['records'][i]['teamRecords'][j]['leagueRecord']['wins']
            info[numTeams]['losses'] = data['records'][i]['teamRecords'][j]['leagueRecord']['losses']
            info[numTeams]['ot'] = data['records'][i]['teamRecords'][j]['leagueRecord']['ot']

            info[numTeams]['gamesPlayed'] = data['records'][i]['teamRecords'][j]['gamesPlayed']

            info[numTeams]['points']= info[numTeams]['wins'] * 2 + info[numTeams]['ot']

            info[numTeams]['teamName'] = data['records'][i]['teamRecords'][j]['team']['name']

            info[numTeams]['teamID'] = TEAM_IDS_LONG[info[numTeams]['teamName']]

            numTeams += 1

    return info


# takes in short team abbreviation, returns list of dicts of stats (0 -> actual numbers, 1 -> relative position (eg. 13))
# other argument decides whether to remove ending (ex. 'th') from ranking, 0 -> 16, 1 -> 16th, defaults to none
def teamStats(team, boolOrdinal=0):

    teamid = TEAM_IDS_SHORT[team]

    url = f"https://statsapi.web.nhl.com/api/v1/teams/{teamid}/stats"

    response = requests.get(url)

    if response.status_code != 200:
        return response.status_code

    data = response.json()

    info = [{},{}]

    for i in [0, 1]:
        for j in data['stats'][i]['splits'][0]['stat'].keys():
            # if adding a ranking (ex. 16th), only add numerical placement as int, else just add it
            if i and not boolOrdinal:
                placementStr = data['stats'][i]['splits'][0]['stat'][j]
                info[i][j] = int(''.join(c for c in placementStr if c.isdigit()))
            else:
                info[i][j] = data['stats'][i]['splits'][0]['stat'][j]

    return info


# takes in nothing (gets current season from const), returns teamStats for all teams (list of dicts)
# sorted by rank
# If wanting 3rd place PK value, then you'd do 'variable[2]['penaltyKill']['value']' - indicies go from 0 to 31 (n = n-1)
def fullTeamStats():

    numTeams = 0

    temp = teamStats(VALID_TEAM)

    # what the value is called converted to what the rank is called (since these are different) (sometimes they use pct vs pctg)
    statNames = {'savePctRank': 'savePctg', 'shootingPctRank': 'shootingPctg'}

    # for sorted data
    # dict with 26 values with length 32 lists in them
    
    # info = [{} for _ in range(TEAMS_IN_LEAGUE)]
    info = [{} for n in range(TEAMS_IN_LEAGUE)]

    # had to fill spot 0 so I could use the ranking as the index
    # info[0]['filler'] = {'filler': 2}

    # gets stats for each team
    for i in TEAM_IDS_SHORT.keys():
        singleTeamStats = teamStats(i)

        for j in singleTeamStats[1].keys():
            if j not in ['penaltyKillOpportunities'] and j not in statNames.keys():
                info[singleTeamStats[1][j] - 1][j] = {'value': singleTeamStats[0][j], 'teamID': int(TEAM_IDS_SHORT[i])}

                if j in ['powerPlayGoals', 'powerPlayOpportunities']:
                    info[singleTeamStats[1][j] - 1][j]['value'] = int(info[singleTeamStats[1][j] - 1][j]['value'])

            elif j in statNames.keys():
                info[singleTeamStats[1][j] - 1][statNames[j]] = {'value': singleTeamStats[0][statNames[j]], 'teamID': int(TEAM_IDS_SHORT[i])}

    return info
    