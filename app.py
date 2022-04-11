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
from user import User 
from schedule import Schedule


from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

#For DB
from flaskext.mysql import MySQL
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
app = Flask(__name__,template_folder='templates')
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
app.config['SERVER_NAME'] = 'localhost:5000'

#Setup db
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'BrickCloudRed#99'
app.config['MYSQL_DATABASE_DB'] = 'social_calendar'
app.config['MYSQL_DATABASE_HOST'] = '34.105.209.85'
mysql.init_app(app)

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute(''' SELECT * FROM user ''')
rows = cursor.fetchall()
 
#Saving the Actions performed on the DB
conn.commit()
 
#Closing the cursor
cursor.close()
print("rows", rows)



# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

SCOPES = [
        "openid", 
        "https://www.googleapis.com/auth/userinfo.email", 
        "https://www.googleapis.com/auth/userinfo.profile", 
        'https://www.googleapis.com/auth/calendar.readonly'
        ]

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id, conn)




#Homepage
@app.route("/")
@app.route("/schedule", methods=["POST", "GET"])
@app.route("/schedule/user=<user_id>", methods=["POST", "GET"])
@app.route("/schedule/date=<start_date>", methods=["POST", "GET"])
@app.route("/schedule/user=<user_id>/date=<start_date>", methods=["POST", "GET"])
def index(user_id=None, start_date=None):
    if current_user.is_authenticated:

        schedule = Schedule(userId = current_user.id, requestStart = start_date, requestUserId = user_id)

        #Initialize variables
        times = []

        #Handle submission of the schedule
        if request.method == 'POST':
            process_schedule(sorted(request.values.getlist('times')))

        # Call the Calendar API   
        service = build('calendar', 'v3', credentials=creds)
        events_result = service.events().list(calendarId='primary', 
                                              timeMin=((schedule.minTime).isoformat() + 'Z'), 
                                              timeMax=((schedule.maxTime).isoformat() + 'Z'),
                                              singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        return render_template("schedule.html", 
            events = schedule.get_events(events),
            schedule=schedule.create_schedule(times),
            title = schedule.title(), 
            prev=schedule.prev_week(),
            next=schedule.next_week())
        
    else:
        return render_template("index.html")


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
        id_=unique_id, name=users_name, email=users_email
    )

    # Doesn't exist? Add it to the database.
    if not User.get(unique_id, conn):
        User.create(unique_id, users_name, users_email, conn)

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

def get_times(user_id, start_date):
    """Get list of free time slots from database corresponding to input user_id and start_date.

    Input parameters:
    user_id int
    start_date date -- Date of the first day in the schedule i.e. the Monday.

    returns:
    list -- Free timeslots for the schedule 
    
    """
    return []

def process_schedule(times:list):
    """Updates database with times the user is free

    Input parameters:
    time list -- array of integer id's corresponding to 1 hour slots where the user is free.

    Return parameters:
    """
    print("Saved times to database: ", times)
    return request
    

def view_friends(friends=[]):
    """Outputs table of friends.

    Input parameters:
    friends tbc

    Returns:
    string -- HTML of freinds table
    """
    return ""
        

if __name__ == "__main__":
    app.run(debug=True)
    
