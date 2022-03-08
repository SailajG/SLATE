# Python standard libraries
import json
import os
import sqlite3

# Third-party libraries
from flask import Flask, redirect, request, url_for
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

        #Get times from database
        times = get_times(0,0)

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
        return '<a class="button" href="/login">Google Login</a>'


#Login page
def get_google_provider_cfg():
    """Add error handling"""
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


#Login callback
@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))
    
    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
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

def process_schedule(times:list):
    """Updates database with times the user is free

    Input parameters:
    time list -- array of integer id's corresponding to 1 hour slots where the user is free.

    Return parameters:
    """
    print("Saved times to database: ", times)
    return request.base_url

if __name__ == "__main__":
    app.run(debug=True)
    

