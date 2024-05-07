# used for debugging functions

import json
from functions import *

# id = playerSearch("josh", "norris", "OTT")

# print(id)

# stats = playerStats(id, "20212022")

# if stats != None:
#     print(stats['goals'])
# else:
#     print("Error: playerStats returned 'None'")

# print(peopleInfo(id))

# temp = allPlayerStats(id)

# temp1 = teamSchedule("Ottawa Senators", "EST")

# standings = getStandings("20212022")

# print(standings)

# print(pytz.all_timezones)

# print(temp1[0])

# print(sys.getrecursionlimit())

# leagueSortedStandings = [{} for _ in range(TEAMS_IN_LEAGUE)]

# sorts standings over whole league
# for i in range(1, TEAMS_IN_LEAGUE):
#     for j in range(TEAMS_IN_LEAGUE):
#         print(f"i = {i} -- rank = {standings[j]['leagueRank']}\n")
#         if int(standings[j]['leagueRank']) == int(i):
#             leagueSortedStandings[i] = standings[j]
#             print(f"applied\n")
#             break

# for m in range(len(leagueSortedStandings)):
#     print(f"{leagueSortedStandings[m]}\n\n")

# for j in range(31):
#     print(standings[j]['leagueRank'])

# leagueSortedStandings[0] = standings[0]

# for g in range(1, 31):
#     print(leagueSortedStandings[g]['wins'])

# tStats = teamStats("WIN")

# print(tStats[1]['powerPlayPercentage'])

# print(tStats['stats'][1]['splits'][0]['stat']['powerPlayPercentage'])

# temp = fullTeamStats()

# print(temp[1]['powerPlayPercentage'])

# temp = {}

# for i in TEAM_IDS_SHORT.keys():
#     temp[TEAM_IDS_SHORT[i]] = i

# print(temp)

# print(playerSearch('Igor', 'Shesterkin'))

# print(json.dumps(allPlayerStats(8484144), indent=4))

# print(json.dumps(peopleInfo(8477939), indent=4))

# print(json.dumps(teamRoster("OTT"), indent=4))

# print(json.dumps(teamSchedule("ott", "America/Toronto"), indent=4))

# print(teamSchedule("ott", "America/Toronto"))

# print(json.dumps(getStandings(), indent=4))

print(json.dumps(teamRoster("ott"), indent=4))