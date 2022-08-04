import requests
import json

# ** ENSURE THIS IS UP TO DATE **
CURRENT_SEASON = '20212022'

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

    for i in data['stats'][0]['splits'][0]['stat'].keys():
        playerInfo[i] = data['stats'][0]['splits'][0]['stat'][i]

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

        temp1 = data['stats'][0]['splits'][i]['season'][:4]
        temp2 = data['stats'][0]['splits'][i]['season'][4:]

        playerInfo[i]['season'] = f"{temp1} - {temp2}"

        playerInfo[i]['team'] = data['stats'][0]['splits'][i]['team']['name']
        playerInfo[i]['league'] = data['stats'][0]['splits'][i]['league']['name']

        for j in data['stats'][0]['splits'][i]['stat'].keys():
            playerInfo[i][j] = data['stats'][0]['splits'][i]['stat'][j]

    return playerInfo

def peopleInfo(id):
    url = f"https://statsapi.web.nhl.com/api/v1/people/{id}"

    response = requests.get(url)

    if response.status_code != 200:
        return 0

    data = response.json()

    info = {}

    # print(data['people'][0].keys())
    # exit()

    for i in data['people'][0].keys():
        if i not in ["currentTeam", "primaryPosition"]:
            info[i] = data['people'][0][i]
    
    info['teamID'] = data['people'][0]['currentTeam']['id']
    info['teamName'] = data['people'][0]['currentTeam']['name']
    info['positionName'] = data['people'][0]['primaryPosition']['name']
    info['positionType'] = data['people'][0]['primaryPosition']['type']
    info['positionAbbreviation'] = data['people'][0]['primaryPosition']['abbreviation']

    return info
