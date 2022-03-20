# Python standard libraries
import json
import os
import sqlite3

import datetime

# Third-party libraries
from flask import Flask, redirect, request, url_for, render_template
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from itsdangerous import NoneAlgorithm
from oauthlib.oauth2 import WebApplicationClient
import requests

# Internal imports
from db import init_db_command
from user import User


from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' #Allows website to use http instead of https

# Get google api details
GOOGLE_CLIENT_ID = "631412287723-9aren88160fka6hivsqith535hhu8c3v.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"

""" Use this after making github public 
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)

if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
    quit("Please add client id and secret to your path and try again")
"""
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

# Flask app setup
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
app.config['SERVER_NAME'] = 'localhost:5000'

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

# Naive database setup
try:
    init_db_command()
except sqlite3.OperationalError:
    # Assume it's already been created
    pass

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

SCOPES = [
        "openid", 
        "https://www.googleapis.com/auth/userinfo.email", 
        "https://www.googleapis.com/auth/userinfo.profile", 
        'https://www.googleapis.com/auth/restndar.readonly'
        ]

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)




#Homepage
@app.route("/")
@app.route("/schedule", methods=["POST", "GET"])
@app.route("/schedule/user=<user_id>", methods=["POST", "GET"])
@app.route("/schedule/date=<start_date>", methods=["POST", "GET"])
@app.route("/schedule/user=<user_id>/date=<start_date>", methods=["POST", "GET"])
def index(user_id=None, start_date=None):
    if current_user.is_authenticated:
        #Initialize variables
        return_body = ""
        times = []

        #Handle submission of the schedule
        if request.method == 'POST':
            process_schedule(sorted(request.values.getlist('times')))

        #Handle viewing of the schedule
    

        info = "<h1>"
        #View other user's schedule
        if user_id != None:
            info += ""+user_id+"'s free time"
            ### Add code here to get user schedule ###
        #View logged-in user's schedule
        else:
            info += "My free time"

        #View schedule for another week
        if start_date != None:
            info += "for week commencing"+start_date+""
        #For schedule for current week.
        else:
            info += "for current week"

        info += "</h1>"

        

        return_body += info

        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        # Prints the start and name of the next 10 events
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            return_body += start
            return_body += event['summary']
        
        return_body += create_schedule(times)

        return (
            "<html><head><title>Schedule</title></head><body>"
            "<p>Hello, {}! You're logged in! Email: {}</p>"
            "<div><p>Google Profile Picture:</p>"
            '<img src="{}" alt="Google profile pic"></img></div>'
            '<a class="button" href="/logout">Logout</a>{}'
            "</body></html>".format(
                current_user.name, current_user.email, current_user.profile_pic,return_body
            )
        )
    else:
        return render_template('index.html')
    


#Login page
def get_google_provider_cfg():
    """Add error handling"""
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route("/login")
def login():
    flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
    
    global creds 
    creds = flow.run_local_server(port=0,redirect_uri_trailing_slash=False)
   
    oauth2_client = build('oauth2', 'v2',credentials=creds)
    user_info = oauth2_client.userinfo().get().execute()

    if user_info["verified_email"]:
        unique_id = user_info["id"]
        users_email = user_info["email"]
        picture = user_info["picture"]
        users_name = user_info["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in your db with the information provided
    # by Google
    user = User(
        id_=unique_id, name=users_name, email=users_email, profile_pic=picture
    )

    # Doesn't exist? Add it to the database.
    if not User.get(unique_id):
        User.create(unique_id, users_name, users_email, picture)

    # Begin user session by logging the user in
    login_user(user)

  
    # Send user back to homepage
    return redirect(url_for("index"))

#Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


def get_times(user_id, start_date):
    """Get list of free time slots from database corresponding to input user_id and start_date.

    Input parameters:
    user_id int
    start_date date -- Date of the first day in the schedule i.e. the Monday.

    returns:
    list -- Free timeslots for the schedule 
    
    """
    return []

def create_schedule(times=[]):
    """Outputs a schedule for the week. Times the user is free are checked.

    Input parameters:
    times list -- array of id's corresponding to 1 hour slots where the user is free. If empty, checkboxes are unchecked.

    Returns:
    str -- HTML string of table
    """
    htmlArray = ["<form action='' method='POST'> <table><tr><th>Time</th><th>Mon</th><th>Tues</th><th>Wed</th><th>Thur</th><th>Fri</th><th>Sat</th><th>Sun</th>"]

    i = 0
    for i in range(7*24):
        
        ### Use something like bootstrap to make the table look nicer
 
        if times != [] and i == int(times[0]):
            checked = "checked"
            del times[0]
        else:
            checked = ""

        label = "time"+str(i)
        checkbox = "<td><input type='checkbox' id='"+label+"' name='times' value="+str(i)+" "+checked+"></td>"

        
        if i % 7 ==  0:
            htmlArray.append("</tr> <tr><th>"+str(int(i/7))+"</th>")

        htmlArray.append("" + checkbox + "")
        
        i = i + 1

    htmlArray.append("</tr></table> <input type='submit' value='Submit'> </form>")

    html = ' '.join(htmlArray)

    return html

def view_friends(friends=[]):
    """Outputs table of friends.

    Input parameters:
    friends tbc

    Returns:
    string -- HTML of freinds table
    """
    return ""

def get_times(user_id, start_date):
    """Get list of free time slots from database corresponding to input user_id and start_date.

    Input parameters:
    user_id int
    start_date date -- Date of the first day in the schedule i.e. the Monday.

    returns:
    list -- Free timeslots for the schedule 
    
    """
    return []

def process_schedule(times):
    """Updates database with times the user is free

    Input parameters:
    time list -- array of integer id's corresponding to 1 hour slots where the user is free.

    Return parameters:
    """
    print("Saved times to database: ", times)
    return request.base_url

if __name__ == "__main__":
    app.run(debug=True)
    
