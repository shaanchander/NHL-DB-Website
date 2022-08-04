from flask import Flask, flash, redirect, render_template, request, session
from functions import *

# TEAMS = []

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/playerSearch", methods = ['GET', 'POST'])
def player_Search():

    curSeason = "20212022"

    if request.method == "GET":
        print("current season: {}".format(CURRENT_SEASON))
        return render_template("playerSearch.html")

    # gets info from form
    fName = request.form.get("fName")
    lName = request.form.get("lName")
    # season = request.form.get("season")


    # gets player id
    id = playerSearch(fName, lName)

    # error traps if player isn't in NHL API db
    if id == 0:
        return render_template("error.html", message = "Player not Found")

    stats = allPlayerStats(id)

    pInfo = peopleInfo(id)

    link = f"http://nhl.bamcontent.com/images/headshots/current/168x168/{id}.jpg"

    return render_template("playerInfo.html", info = stats, numYears = len(stats), person = pInfo, imgLink = link)

@app.route("/teamSearch")
def team_Search():
    return render_template("teamSearch.html")

@app.route("/schedule")
def schedule():
    return render_template("schedule.html")