from flask import Flask, flash, redirect, render_template, request, session
from functions import *

TEAMS = []

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/playerSearch", methods = ['GET', 'POST'])
def player_Search():

    if request.method == "GET":
        return render_template("playerSearch.html")

    # gets info from form
    fName = request.form.get("fName")
    lName = request.form.get("lName")
    # team = request.form.get("team")
    season = request.form.get("season")


    # if team == "":
    #     team = 0

    # gets player id
    id = playerSearch(fName, lName)

    # error traps if player isn't in NHL API db
    if id == 0:
        return render_template("error.html")

    if season == "":
        stats = playerStats(id)
    else:
        stats = playerStats(id, season)

    return render_template("playerInfo.html", info = stats)

@app.route("/teamSearch")
def team_Search():
    return render_template("teamSearch.html")

@app.route("/schedule")
def schedule():
    return render_template("schedule.html")