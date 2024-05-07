from flask import render_template
import requests
from datetime import datetime, date
import pytz

# ** ENSURE THESE CONSTANTS ARE UP TO DATE **
CURRENT_SEASON = '20232024'

# east, west
TEAMS_IN_CONFERENCE = [16, 16]

# atlantic, metro, central, pacific
TEAMS_IN_DIV = [8, 8, 8, 8]
DIV_NAMES = ['Atlantic', 'Metropolitan', 'Central', 'Pacific']

TEAMS_IN_LEAGUE = 32

TEAM_IDS_SHORT = {"ANA":24, "ARI":53, "BOS":6, "BUF":7, "CGY":20, "CAR":12, "CHI":16, "COL":21, "CBJ":29, "DAL":25, "DET":17, "EDM":22, "FLA":13, "LAK":26, "MIN":30, "MTL":8, "NSH":18, "NJD":1, "NYI":2, "NYR":3, "OTT":9, "PHI":4, "PIT":5, "SJS":28, "SEA":55, "STL":19, "TBL":14, "TOR":10, "VAN":23, "VGK":54, "WSH":15, "WPG":52}

TEAM_IDS_LONG = {"Anaheim Ducks":24, "Arizona Coyotes":53, "Boston Bruins":6, "Buffalo Sabres":7, "Calgary Flames":20, "Carolina Hurricanes":12, "Chicago Blackhawks":16, "Colorado Avalanche":21, "Columbus Blue Jackets":29, "Dallas Stars":25, "Detroit Red Wings":17, "Edmonton Oilers":22, "Florida Panthers":13, "Los Angeles Kings":26, "Minnesota Wild":30, "Montréal Canadiens":8, "Nashville Predators":18, "New Jersey Devils":1, "New York Islanders":2, "New York Rangers":3, "Ottawa Senators":9, "Philadelphia Flyers":4, "Pittsburgh Penguins":5, "San Jose Sharks":28, "Seattle Kraken":55, "St. Louis Blues":19, "Tampa Bay Lightning":14, "Toronto Maple Leafs":10, "Vancouver Canucks":23, "Vegas Golden Knights":54, "Washington Capitals":15, "Winnipeg Jets":52}

REV_TEAM_IDS_LONG = {24: "Anaheim Ducks", 53: "Arizona Coyotes", 6: "Boston Bruins", 7: "Buffalo Sabres", 20: "Calgary Flames", 12: "Carolina Hurricanes", 16: "Chicago Blackhawks", 21: "Colarado Avalanche", 29: "Columbus Blue Jackets", 25: "Dallas Stars", 17: "Detroit Red Wings", 22: "Edmonton Oilers", 13: "Florida Panthers", 26: "Los Angeles Kings", 30: "Minnesota Wild", 8: "Montréal Canadiens", 18: "Nashville Predators", 1: "New Jersey Devils", 2: "New York Islanders", 3: "New York Rangers", 9: "Ottawa Senators", 4: "Philadelphia Flyers", 5: "Pittsbirgh Penguins", 28: "San Jose Sharks", 55: "Seattle Kraken", 19: "St. Louis Blues", 14: "Tampa Bay Lightning", 10: "Toronto Maple Leafs", 23: "Vancouver Canucks", 54: "Vegas Golden Knights", 15: "Washington Capitals", 52: "Winnipeg Jets"}

REV_TEAM_IDS_SHORT = {24: 'ANA', 53: 'ARI', 6: 'BOS', 7: 'BUF', 20: 'CGY', 12: 'CAR', 16: 'CHI', 21: 'COL', 29: 'CBJ', 25: 'DAL', 17: 'DET', 22: 'EDM', 13: 'FLA', 26: 'LAK', 30: 'MIN', 8: 'MTL', 18: 'NSH', 1: 'NJD', 2: 'NYI', 3: 'NYR', 9: 'OTT', 4: 'PHI', 5: 'PIT', 28: 'SJS', 55: 'SEA', 19: 'STL', 14: 'TBL', 10: 'TOR', 23: 'VAN', 54: 'VGK', 15: 'WSH', 52: 'WPG'}

VALID_TEAM = 'ANA'

# TEAM_IDS = [1,2,3,4,5,6,7,8,9,10,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,28,29,30,52,53,54]

POSITION_CONV = {'G': 'Goalie', 'L': 'Left Wing', 'R': 'Right Wing', 'C': 'Centre', 'D': 'Defenseman'}



#TODO

# Use '/now' instead of CURRENT_SEASON



# takes in player info, returns id, if no player is found, returns 0
def playerSearch(fName, lName, team = '0'):

    fName = fName.lower()
    lName = lName.lower()

    # url = f'https://suggest.svc.nhl.com/svc/suggest/v1/minplayers/{fName} {lName}'
    url = f'https://search.d3.nhle.com/api/v1/search/player?culture=en-us&limit=20&q={fName} {lName}'

    response = requests.get(url)

    if response.status_code != 200:
        return 0

    data = response.json()

    # for i in range(len(data['suggestions'])):
    #     data['suggestions'][i] = data['suggestions'][i].split('|')

    # # doesn't filter by team if one isn't provided
    # if team == '0':
    #     for i in range(len(data['suggestions'])):
    #         data['suggestions'][i][11] = '0'

    # # checks list of returned players, returning the ID of the one with the same fName, lName, and team (if provided) as passed into the function
    # for i in range(len(data['suggestions'])):
    #     if data['suggestions'][i][2].lower() == fName and data['suggestions'][i][1].lower() == lName and team == data['suggestions'][i][11]:
    #         return data['suggestions'][i][0]

    # if not team specific search
    if team == '0':
        for i in data:
            print(i['name'])
            if i['name'].replace(' ', '').lower() == f"{fName}{lName}".replace(' ', '').lower():
                return i['playerId']

    # if specific team included in search      
    else:
        for i in data:
            if i['name'] == f"{fName} {lName}" and team == i['teamAbbrev']:
                return i['playerId']

    return 0


# takes in player ID and the season (if not provided, defaults to current season), returns dict of stats, returns list of lists from all entries matching given season (NHL, WJC, etc.)
def playerStats(id, season = CURRENT_SEASON, gameType=2):

    # url = f"https://statsapi.web.nhl.com/api/v1/people/{id}/stats?stats=statsSingleSeason&season={season}"

    seasonStats = []

    url = f"https://api-web.nhle.com/v1/player/{id}/landing"

    response = requests.get(url)

    if response.status_code != 200:
        return 0

    data = response.json()

    # print(len(data['seasonTotals']))

    for i in data['seasonTotals']:

        # print(str(season) + "      " + str(i['season']))
        if str(i['season']) == str(season):
            seasonStats.append(i)
            # print("lets")
            

    playerInfo = []

    # gameType ----  1 = prob preseson, 2 = regular season, 3 = playoffs
    
    # if they don't have an id or stats? (some kind of error trapping)
    # if i['gamesPlayed']:
    #     playerInfo['goals'] = "-"
    #     playerInfo['assists'] = "-"
    #     playerInfo['points'] = "-"
    #     playerInfo['plusMinus'] = "-"

    #     playerInfo['savePercentage'] = "-"
    #     playerInfo['goalAgainstAverage'] = "-"

    #     return playerInfo
    
    # TODO make this error trap with missing stats

    # try:
    #     # playerInfo[i]['goalAgainstAverage'] = round(playerInfo[i]['goalAgainstAverage'], 2)
    #     playerInfo['goalAgainstAverage'] =  "%0.2f" % round(float(playerInfo['goalAgainstAverage']), 2)
    #     # playerInfo[i]['savePercentage'] =  "%0.3f" % round(playerInfo[i]['savePercentage'], 3)

    #     for k in ["goalAgainstAverge", "wins", "savePercentage"]:
    #         if k not in playerInfo.keys():
    #             playerInfo[k] = '-'
    #         elif k == "savePercentage":
    #             playerInfo['savePercentage'] =  "%0.3f" % round(playerInfo['savePercentage'], 3)

    #     if playerInfo['savePercentage'][:3] == "0.0":
    #         playerInfo['savePercentage'] = '-'
                
    # # if they are a skater
    # except KeyError:
    #     for k in ["games", "goals", "assists", "points", "plusMinus"]:
    #         if k not in playerInfo.keys():
    #             playerInfo[k] = '-'

    # for each season with matching season as given
    for i in seasonStats:

        singleSeason = {}

        # if goalie
        if 'goalsAgainst' in i.keys():

            for j in ['goalsAgainstAvg', 'savePctg', 'wins', 'gamesPlayed']:
                try:
                    singleSeason[j] = i[j]
                except:
                    singleSeason[j] = '-'

            try:
                singleSeason['savePctg'] = round(float(singleSeason['savePctg']), 3)
            except:
                pass

            try:
                singleSeason['goalsAgainstAvg'] = round(singleSeason['goalsAgainstAvg'], 2)
            except:
                pass

        
        # if skater (not goalie)
        else:
            for j in ['goals', 'assists', 'points', 'plusMinus', 'pim', 'gamesPlayed']:
                try:
                    singleSeason[j] = i[j]
                except:
                    singleSeason[j] = '-'

        # formats season
        singleSeason['seasonStartYear'] = str(i['season'])[:4]
        singleSeason['seasonEndYear'] = str(i['season'])[4:]

        # if given stats are playoffs
        if i['gameTypeId'] == 3:
            singleSeason['season'] = f"{singleSeason['seasonStartYear']} - {singleSeason['seasonEndYear']} (Playoffs)"
        else:
            singleSeason['season'] = f"{singleSeason['seasonStartYear']} - {singleSeason['seasonEndYear']}"


        # gets league and team names
        singleSeason['team'] = i['teamName']['default']
        singleSeason['league'] = i['leagueAbbrev']

        playerInfo.append(singleSeason)

    return playerInfo

# takes in player id, returns list of list of dicts for stats from each season/league
def allPlayerStats(id):

    # url = f"https://statsapi.web.nhl.com/api/v1/people/{id}/stats?stats=yearByYear"

    url = f"https://api-web.nhle.com/v1/player/{id}/landing"

    response = requests.get(url)

    if response.status_code != 200:
        return 0

    data = response.json()['seasonTotals']

    playerInfo = []

    seasonLog = []

    for i in range(len(data)):

        if data[i]['season'] not in seasonLog:

            temp = playerStats(id, data[i]['season'], data[i]['gameTypeId'])

            for entry in temp:
                playerInfo.append(entry)

            seasonLog.append(data[i]['season'])

    return playerInfo

# gets player personal info
def peopleInfo(id):
    # url = f"https://statsapi.web.nhl.com/api/v1/people/{id}"

    url = f"https://api-web.nhle.com/v1/player/{id}/landing"

    response = requests.get(url)

    if response.status_code != 200:
        return 0

    data = response.json()

    info = {}

    for i in data.keys():

        if type(data[i]) != list and type(data[i]) != dict:
            info[i] = data[i]

        info['fullName'] = data['firstName']['default'] + " " + data['lastName']['default']

        info['birthCity'] = data['birthCity']['default']
        info['birthCountry'] = data['birthCountry']

        info['birthDate'] = data['birthDate']

        # info['birthLocationFull'] = f"{data['birthCity']['default']}, {data['birthCountry']}"

        info['heightFull'] = f"{int(data['heightInInches']/12)}' {data['heightInInches'] % 12}\""

        try:
            info['teamName'] = data['fullTeamName']['default']
        except:
            pass

        info['positionFull'] =  POSITION_CONV[data['position']]

        today = date.today()

        info['age'] = today.year - int(info['birthDate'].split('-')[0]) - ((today.month, today.day) < (int(info['birthDate'].split('-')[1]), int(info['birthDate'].split('-')[2]))) 

    # # gets 
    # for i in data['people'][0].keys():
    #     if i not in ["currentTeam", "primaryPosition"]:
    #         info[i] = data['people'][0][i]

    # # tries to get team information
    # try:
    #     info['teamID'] = data['people'][0]['currentTeam']['id']
    #     info['teamName'] = data['people'][0]['currentTeam']['name']
    # except KeyError:
    #     pass

    # gets position info
    info['positionName'] = data['position']
    # info['positionType'] = data['people'][0]['primaryPosition']['type']
    # info['positionAbbreviation'] = data['people'][0]['primaryPosition']['abbreviation']

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
    info['logoUrl'] = f"https://assets.nhle.com/logos/nhl/svg/{team}_light.svg"

    return info

# gets team roster info
def teamRoster(team):

    # teamID = TEAM_IDS_SHORT[team]

    # url = f"https://statsapi.web.nhl.com/api/v1/teams/{teamID}/roster"

    url = f"https://api-web.nhle.com/v1/roster/{team}/current"

    response = requests.get(url)

    if response.status_code != 200:
        return 0

    data = response.json()

    # creates list of dicts
    # info = [{} for _ in range(len(data['roster']))]
    info = []


    for position in data:

        # for each roster player
        for player in range(len(data[position])):


            curPlayer = peopleInfo(data[position][player]['id'])
            curPlayer['stats'] = playerStats(data[position][player]['id'])

            # info.append(peopleInfo(data[position][player]['id'])['stats'].update(playerStats(data[position][player]['id'])))

            info.append(curPlayer)

            # print(player)

            # just because why not
            # if info[i]['name'] == "Tim Stützle":
            #     info[i]['name'] = "Tim 'Pentagon' Stützle"

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
    # teamID = TEAM_IDS_LONG[team]

    # url = f"https://statsapi.web.nhl.com/api/v1/schedule?teamId={teamID}&season={season}"
    # url = f"https://api-web.nhle.com/v1/club-schedule-season/{team}/{CURRENT_SEASON}"
    url = f"https://api-web.nhle.com/v1/club-schedule-season/{team}/now"

    response = requests.get(url)

    if response.status_code != 200:
        return response.status_code

    data = response.json()['games']

    info = []

    # initializes counters
    totalGamesIndex = 0
    dayIndex = 0
    gameIndex = 0

    for game in data:

        curGame = {}

        dateTime = game['startTimeUTC']

        # gets time in UTC of game
        year = int(dateTime[:4])
        month = int((dateTime)[5:7]) 
        day = int(dateTime[8:10])
        hour = int(dateTime[11:13])
        minute = int(dateTime[14:16])
        
        # converts date and time to selected timezone
        tempDate = datetime(year, month, day, hour, minute)
        tempDate = utc_to_time(tempDate, timeZone)

        curGame['gameDate'] = tempDate.strftime("%b %d, %Y")
        curGame['gameTime'] = tempDate.strftime("%I:%M%p")

        # gets remaining game info
        curGame['gameType'] =  game['gameType']
        curGame['venueName'] = game['venue']['default']
        curGame['awayTeamName'] = game['awayTeam']['abbrev']
        curGame['awayTeamId'] = game['awayTeam']['id']
        curGame['homeTeamName'] = game['homeTeam']['abbrev']
        curGame['homeTeamId'] = game['homeTeam']['id']
        curGame['gameStatus'] = game['gameState']

        info.append(curGame)

    return info

# gets standings data (including wins, losses, etc.), gets from given season, if none given, defaults to current
# returns stats dict (with wins, full team name, pts, etc.) and standings dict with standing by league, conference, and division
def getStandings(season = CURRENT_SEASON):

    # season = "20212022"

    # url = f"https://statsapi.web.nhl.com/api/v1/standings?season={season}"
    url = f"https://api-web.nhle.com/v1/standings/now"

    response = requests.get(url)

    if response.status_code != 200:
        return response.status_code

    data = response.json()['standings']

    leagueStandings = []
    conferenceStandings = {'Eastern':[], 'Western':[]}
    divisionStandings = {DIV_NAMES[0]:[], DIV_NAMES[1]:[], DIV_NAMES[2]: [], DIV_NAMES[3]: []}

    # get order of teams, sort into lists by league, conference, and division
    for place in range(1, TEAMS_IN_LEAGUE):
        for team in data:

            if team['leagueSequence'] == place:
                leagueStandings.append(team['teamAbbrev']['default'])

            if team['conferenceSequence'] == place:
                conferenceStandings[team['conferenceName']].append(team['teamAbbrev']['default'])

            if team['divisionSequence'] == place:
                divisionStandings[team['divisionName']].append(team['teamAbbrev']['default'])

    standings = {'league': leagueStandings, 'conference': conferenceStandings, 'division': divisionStandings}

    
    teamStats = {}

    # get stats (pts, wins, etc.) of all teams to display in standings
    for team in data:

        curTeam = {}

        curTeam['wins'] = team['wins']
        curTeam['losses'] = team['losses']
        curTeam['ot'] = team['otLosses']
        curTeam['gamesPlayed'] = team['gamesPlayed']
        curTeam['points']= team['points']
        curTeam['teamName'] = team['teamName']['default']

        curTeam['logo'] = team['teamLogo']

        teamStats[team['teamAbbrev']['default']] = curTeam

    return {'standings': standings, 'stats': teamStats}


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
    