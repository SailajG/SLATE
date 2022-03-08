from flask import Flask, request
import lib as l

app = Flask(__name__)

@app.route("/login", methods=["POST", "GET"])

def login():
    """Login page

    Returns:
    str - HTML of returned web-page
    """
    return_value = '''
            <html>
                <head>
                    <title>Login</title>
                </head>
                <body>
                    <h1> Login </h1>
                </body>
            </html>'''

    return return_value

@app.route("/friends", methods=["POST", "GET"])
def friends():
    """List of logged-in user's friends with CRUD functionality

    Returns:
    str - HTML of returned web-page
    """

    return_value = '''
            <html>
                <head>
                    <title>Friends</title>
                </head>
                <body>
                    <h1> My Friends </h1>
                    '''+l.view_friends()+'''
                </body>
            </html>'''

    return return_value

@app.route("/", methods=["POST", "GET"]) #Possibly use a different function for this app route
@app.route("/schedule", methods=["POST", "GET"])
@app.route("/schedule/user=<user_id>", methods=["POST", "GET"])
@app.route("/schedule/date=<start_date>", methods=["POST", "GET"])
@app.route("/schedule/user=<user_id>/date=<start_date>", methods=["POST", "GET"])

def schedule(user_id=None, start_date=None):
    """Handles HTTP requests to the schedule page.

    Input parameters:
    user_id int -- User to show schedule for. If None, the logged-in user is shown.
    start_date date -- Week start date to show schedule for. If None, the current week's schedule is shown.

    Returns:
    str - HTML of returned web-page
    """
    #times =[ '2', '4', '7', '9', '10', '11', '13', '15', '16', '21', '22', '23', '26', '27', '28', '29', '31', '32', '34', '36', '39', '41', '44', '45', '47', '51', '53', '54', '55', '56', '57', '59', '61', '62', '64', '65', '66', '67', '68', '73', '74', '75', '76', '79', '80', '82', '83', '88', '89', '90', '91', '96', '99', '104', '105', '107', '111', '112', '113', '114', '116', '118', '120', '122', '123', '128', '129', '130', '131', '133', '136', '139', '141', '142', '147', '148', '149', '152', '153', '154', '155', '156', '158', '159', '161', '162', '163', '164', '165', '167']

    #Initialize variables
    return_body = ""
    times = []

    #Handle submission of the schedule
    if request.method == 'POST':
        l.process_schedule(sorted(request.values.getlist('times')))

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
    times = l.get_times(0,0)

    return_body += l.create_schedule(times)
    return_value = '''
        <html>
            <head>
                <title>Schedule</title>
            </head>
            <body>
                '''+return_body+'''
            </body>
        </html>'''

    return return_value