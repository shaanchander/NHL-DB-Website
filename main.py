import requests
import json

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