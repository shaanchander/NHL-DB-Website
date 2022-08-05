from functions import *

id = playerSearch("josh", "norris", "OTT")

print(id)

stats = playerStats(id, "20212022")

if stats != None:
    print(stats['goals'])
else:
    print("Error: playerStats returned 'None'")

# print(peopleInfo(id))

temp = allPlayerStats(id)

temp1 = teamSchedule("OTT", "EST")

# print(pytz.all_timezones)

# print(temp1[0])