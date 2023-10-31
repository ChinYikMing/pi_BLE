from flask import Flask, render_template
import os

app = Flask(__name__)

# people counter file
people_counter_filename = "../people_counter"
people_counter_file = open(people_counter_filename, "r")
people_counter = int(people_counter_file.readline())
#print(people_counter)

@app.route("/")
def index():
    return render_template("index.html", people_counter=people_counter)
    #return "<p>Hello, World!</p>"
