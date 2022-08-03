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
        return None

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

    return None


# takes in player ID and the season (if not provided, defaults to current season), returns dict of stats
def playerStats(id, season = CURRENT_SEASON):

    url = f"https://statsapi.web.nhl.com/api/v1/people/{id}/stats?stats=statsSingleSeason&season={season}"

    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()

    playerInfo = {}

    for i in data['stats'][0]['splits'][0]['stat'].keys():
        playerInfo[i] = data['stats'][0]['splits'][0]['stat'][i]

    return playerInfo