from flask import Flask, render_template
from flask import jsonify
from flask import Response
import os

app = Flask(__name__)

@app.route("/")
def index():
    people_counter_filename = "./people_counter"
    people_counter_file = open(people_counter_filename, "r")
    people_counter = int(people_counter_file.readline())
    return render_template("index.html", people_counter=people_counter)

@app.route("/peopleCounter")
def peopleCounter():
    people_counter_filename = "./people_counter"
    people_counter_file = open(people_counter_filename, "r")
    people_counter = people_counter_file.readline()
    return Response(str(people_counter), mimetype='text/plain')
