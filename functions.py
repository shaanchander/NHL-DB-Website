from calendar import month
from ctypes.wintypes import HMODULE
from unicodedata import name
from flask import render_template
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
import pytz

# ** ENSURE THIS IS UP TO DATE **
CURRENT_SEASON = '20222023'

TEAM_IDS = {"ANA":24, "ARI":53, "BOS":6, "BUF":7, "CGY":20, "CAR":12, "CHI":16, "COL":21, "CBJ":29, "DAL":25, "DET":17, "EDM":22, "FLA":13, "LAK":26, "MIN":30, "MTL":8, "NSH":18, "NJD":1, "NYI":2, "NYR":3, "OTT":9, "PHI":4, "PIT":5, "SJS":28, "SEA":55, "STL":19, "TBL":14, "TOR":10, "VAN":23, "VGK":54, "WSH":15, "WIN":52}

# TEAM_IDS = [1,2,3,4,5,6,7,8,9,10,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,28,29,30,52,53,54]

# takes in player info, returns id, if no player is found, returns 0
def playerSearch(fName, lName, team = '0'):

    # fName = fName.lower()
    # lName = lName.lower()

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

    if info['fullName'] == "Tim Stützle":
        info['fullName'] = "Tim 'Pentagon' Stützle"

    return info

# gets team info
def teamInfo(team):

    teamID = TEAM_IDS[team]

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

    teamID = TEAM_IDS[team]

    url = f"https://statsapi.web.nhl.com/api/v1/teams/{teamID}/roster"

    response = requests.get(url)

    if response.status_code != 200:
        return 0

    data = response.json()

    info = [{} for _ in range(len(data['roster']))]

    for i in range(len(data['roster'])):
        info[i]['name'] = data['roster'][i]['person']['fullName']

        if info[i]['name'] == "Tim Stützle":
            info[i]['name'] = "Tim 'Pentagon' Stützle"
        try:
            info[i]['number'] = f"#{data['roster'][i]['jerseyNumber']}"
        except KeyError:
            info[i]['number'] = '-'

        info[i]['id'] = data['roster'][i]['person']['id']
        info[i]['positionName'] = data['roster'][i]['position']['name']
        info[i]['positionType'] = data['roster'][i]['position']['type']
        info[i]['positionAbbreviation'] = data['roster'][i]['position']['abbreviation']

        info[i]['stats'] = playerStats(info[i]['id'])

    return info

def utc_to_time(naive, timezone="Europe/Istanbul"):
    return naive.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(timezone))

# gets a team's schedule
def teamSchedule(team, timeZone, season = CURRENT_SEASON):

    if team == '0':
        return render_template("error.html", message = "Team not Found")

    teamID = TEAM_IDS[team]

    url = f"https://statsapi.web.nhl.com/api/v1/schedule?teamId={teamID}&season={season}"

    response = requests.get(url)

    if response.status_code != 200:
        return response.status_code

    data = response.json()

    info = [{} for _ in range(data['totalGames'])]

    totalGamesIndex = 0

    dayIndex = 0
    gameIndex = 0

    while 1:

        # info[totalGamesIndex]['gameDate'] = data['dates'][dayIndex]['games'][gameIndex]['gameDate']

        # info[totalGamesIndex]['gameTime'] = data['dates'][dayIndex]['games'][gameIndex]['gameDate']

        dateTime = data['dates'][dayIndex]['games'][gameIndex]['gameDate']

        # print(datetime.timestamp(info[totalGamesIndex]['gameDate'], tz=None))
        # exit

        year = int(dateTime[:4])
        month = int((dateTime)[5:7]) 
        day = int(dateTime[8:10])
        hour = int(dateTime[11:13])
        minute = int(dateTime[14:16])
        # second = int(dateTime[17:19])

        # print(second)
        # exit

        tempDate = datetime(year, month, day, hour, minute)

        tempDate = utc_to_time(tempDate, timeZone)

        info[totalGamesIndex]['gameDate'] = tempDate.strftime("%b %d, %Y")
        info[totalGamesIndex]['gameTime'] = tempDate.strftime("%I:%M%p")

        # tz = pytz.timezone(timeZone)
        # utc = pytz.utc

        # tempDate = tz.localize(tempDate)

        # print(tempDate)
        # exit()

        # pytz.utc.localize(utc_time, is_dst=None).astimezone(timeZone)

        # utc = ZoneInfo('UTC')
        # tz = ZoneInfo(timeZone)

        # localtime = utctime.astimezone(localtz)

        # utc_unaware = datetime(year, month, day, hour, minute)
        # utc_aware = utc_unaware.replace(tzinfo=ZoneInfo('UTC'))  
        # local_aware = utc_aware.astimezone(ZoneInfo('EST'))

        # print(local_aware)
        # exit()

        # info[totalGamesIndex]['gameDate'] = local_aware.strftime("%b %d, %Y")
        # info[totalGamesIndex]['gameTime'] = local_aware.strftime("%I:%M%p")

        # print(finalTime)
        # exit()

        # dateTimeString = f"{year}-{month}-{day} {hour}:{minute}:{second}"
        # dateTimeObject = datetime.strptime(dateTimeString, '%Y-%m-%d %H:%M:%S')

        # epochSeconds = dateTimeObject.timestamp()

        # finalTime = epochSeconds.strftime("%b %d %Y at %I:%M%p")

        # info[totalGamesIndex]['gameDate'] = 

        # info[totalGamesIndex]['gameTime'] = 

        info[totalGamesIndex]['gameType'] =  data['dates'][dayIndex]['games'][gameIndex]['gameType']
        info[totalGamesIndex]['venueName'] = data['dates'][dayIndex]['games'][gameIndex]['venue']['name']
        info[totalGamesIndex]['awayTeamName'] = data['dates'][dayIndex]['games'][gameIndex]['teams']['away']['team']['name']
        info[totalGamesIndex]['awayTeamId'] = data['dates'][dayIndex]['games'][gameIndex]['teams']['away']['team']['id']
        info[totalGamesIndex]['homeTeamName'] = data['dates'][dayIndex]['games'][gameIndex]['teams']['home']['team']['name']
        info[totalGamesIndex]['homeTeamId'] = data['dates'][dayIndex]['games'][gameIndex]['teams']['home']['team']['id']
        info[totalGamesIndex]['gameStatus'] = data['dates'][dayIndex]['games'][gameIndex]['status']['detailedState']

        if gameIndex < len(data['dates'][dayIndex]['games']) - 1: 
            gameIndex += 1
        else:
            dayIndex += 1
            gameIndex = 0

        totalGamesIndex += 1

        if totalGamesIndex >= data['totalGames']:
            break

    return info

# def standings():
