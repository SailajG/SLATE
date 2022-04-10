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

# For DB
from flaskext.mysql import MySQL

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Allows website to use http instead of https

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
app = Flask(__name__, template_folder='templates')
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
app.config['SERVER_NAME'] = '127.0.0.1:5000'

# Setup db
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

# Saving the Actions performed on the DB
conn.commit()

# Closing the cursor
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


# Handle GET requests for schedule
@app.route("/")
@app.route("/schedule", methods=["POST", "GET"])
@app.route("/schedule/user=<user_id>", methods=["POST", "GET"])
@app.route("/schedule/date=<start_date>", methods=["POST", "GET"])
@app.route("/schedule/user=<user_id>/date=<start_date>", methods=["POST", "GET"])
def index(user_id=None, start_date=None):
    if current_user.is_authenticated:
        print("logged-in")
        schedule = Schedule(userId=current_user.id, requestStart=start_date, requestUserId=user_id)

        # Initialize variables
        times = []

        # Call the Calendar API   
        service = build('calendar', 'v3', credentials=creds)
        events_result = service.events().list(calendarId='primary',
                                              timeMin=((schedule.minTime).isoformat() + 'Z'),
                                              timeMax=((schedule.maxTime).isoformat() + 'Z'),
                                              singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        return render_template("index.html",
                               schedule=schedule.create_schedule(times, events, conn),
                               title=schedule.title(),
                               prev=schedule.prev_week(),
                               next=schedule.next_week())

    else:
        print("Log-in")
        return render_template("index.html")


# Login page
def get_google_provider_cfg():
    """Add error handling"""
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route("/login")
def login():
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES)

    global creds
    creds = flow.run_local_server(port=0, redirect_uri_trailing_slash=False)

    oauth2_client = build('oauth2', 'v2', credentials=creds)
    user_info = oauth2_client.userinfo().get().execute()

    if user_info["verified_email"]:
        unique_id = user_info["id"]
        users_email = user_info["email"]
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


# Logout
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


""" Sailaj did add his code here ;-) """


@app.route("/schedule/delete/user=<user_id>/date=<start_date>", methods=["POST", "GET"])
def delete_schedule(user_id, start_date):
    """
    """
    print("user_id", current_user.id)
    print("start_date", start_date)

    # Check that the table exists before attempting to insert any records
    sql = """SELECT * FROM information_schema.columns
                 WHERE table_schema = 'social_calendar' 
                    AND table_name = 'user_schedule'
                 LIMIT 1;"""
    cursor.execute(sql)
    response = cursor.fetchone()
    if response is not None:
        print(f'DB Table Exists: {response}')
        sql = "DELETE FROM user_schedule WHERE user_id = %s, week_start_date = %s , free_time = %s"
        for row in sorted(request.values.getlist('times')):
            data = (current_user.id, start_date, row)
            print(f'Each Record: {data}')
            cursor.execute(sql, data)
        conn.commit()
    else:
        print('DB Table does not exist. Delete Aborted!')

    return redirect(url_for("index"))


@app.route("/schedule/add/user=<user_id>/date=<start_date>", methods=["POST", "GET"])
def insert_schedule(user_id, start_date):
    """
    """
    print("user_id", current_user.id)
    print("start_date", start_date)
    print("free_times", sorted(request.values.getlist('times')))

    cursor = conn.cursor()

    # Create table if not exists
    sql = """create table if not exists user_schedule
            (
                user_id         int       not null,
                week_start_date varchar(10)      not null,
                free_time       varchar(10)       not null,
                primary key (user_id, week_start_date, free_time)
            )"""
    cursor.execute(sql)
    conn.commit()

    # Check that the table exists before attempting to insert any records
    sql = """SELECT * FROM information_schema.columns
             WHERE table_schema = 'social_calendar' 
                AND table_name = 'user_schedule'
             LIMIT 1;"""
    cursor.execute(sql)
    response = cursor.fetchone()
    if response is not None:
        print(f'DB Table Exists: {response}')
        sql = "INSERT INTO user_schedule(user_id, week_start_date, free_time) VALUES (%s, %s, %s)"
        for row in sorted(request.values.getlist('times')):
            data = (current_user.id, start_date, row)
            print(f'Each Record: {data}')
            cursor.execute(sql, data)
        conn.commit()
    else:
        print('DB Table does not exist. Insert Aborted!')

    return redirect("/schedule/date=" + str(start_date))


@app.route("/schedule/update/user=<user_id>/date=<start_date>", methods=["POST", "GET"])
def update_schedule(user_id, start_date):
    """
    """
    print("user_id", current_user.id)
    print("start_date", request.args.get('date'))
    print("free_times", sorted(request.values.getlist('times')))

    # Check that the table exists before attempting to insert any records
    sql = """SELECT * FROM information_schema.columns
                 WHERE table_schema = 'social_calendar' 
                    AND table_name = 'user_schedule'
                 LIMIT 1;"""
    cursor.execute(sql)
    response = cursor.fetchone()
    if response is not None:
        print(f'DB Table Exists: {response}')
        sql = "REPLACE INTO user_schedule(user_id,week_start_date,free_time) VALUES (%s %s %s)"
        for row in sorted(request.values.getlist('times')):
            data = (current_user.id, start_date, row)
            print(f'Each Record: {data}')
            cursor.execute(sql, data)
        conn.commit()
    else:
        print('DB Table does not exist. Update Aborted!')

    return redirect("/schedule/date=" + str(request.args.get('date')))


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
