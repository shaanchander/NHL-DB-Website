import requests
import json

from functions import *

id = playerSearch("thomas", "chabot", "OTT")

print(id)

print(playerStats(id, "goals", "20202021"))