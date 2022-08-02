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

    data = response.json()

    for i in range(len(data['suggestions'])):
        data['suggestions'][i] = data['suggestions'][i].split('|')

    # print(data['suggestions'][0][0])
    # exit()

    # doesn't filter by team if one isn't provided
    if team == '0':
        for i in range(len(data['suggestions'])):
            data['suggestions'][i][11] = '0'

    # checks list of returned players, returning the ID of the one with the same fName, lName, and team (if provided) as passed into the function
    for i in range(len(data['suggestions'])):
        if data['suggestions'][i][2].lower() == fName and data['suggestions'][i][1].lower() == lName and team == data['suggestions'][i][11]:
            return data['suggestions'][i][0]

        # print(data['suggestions'][i][2].lower())
        # print(fName)

        # print(data['suggestions'][i][1].lower())
        # print(lName)

        # print(data['suggestions'][i][11])
        # print(team)

        # print(f"\n")

    

    return 0

# takes in player ID, the stat you want (ex. 'goals', 'pim'), and the season (if not provided, defaults to current season), returns stat
def playerStats(id, stat, season = CURRENT_SEASON):

    url = f'https://statsapi.web.nhl.com/api/v1/people/{id}/stats?stats=statsSingleSeason&season={season}'

    response = requests.get(url)

    data = response.json()

    return data['stats'][0]['splits'][0]['stat'][stat]