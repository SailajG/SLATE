from flask import Flask, request
from datetime import date

def process_schedule(times:list):
    """Updates database with times the user is free

    Input parameters:
    time list -- array of integer id's corresponding to 1 hour slots where the user is free.

    Return parameters:
    """
    print("Saved times to database: ", times)
    return request.base_url

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

def get_times(user_id:int, start_date:date):
    """Get list of free time slots from database corresponding to input user_id and start_date.

    Input parameters:
    user_id int
    start_date date -- Date of the first day in the schedule i.e. the Monday.

    returns:
    list -- Free timeslots for the schedule 
    
    """
    return []

if __name__ == "__main__":
    #Test programme
    #t=['2', '4', '7', '9', '10', '11', '13', '15', '16', '21', '22', '23', '26', '27', '28', '29', '31', '32', '34', '36', '39', '41', '44', '45', '47', '51', '53', '54', '55', '56', '57', '59', '61', '62', '64', '65', '66', '67', '68', '73', '74', '75', '76', '79', '80', '82', '83', '88', '89', '90', '91', '96', '99', '104', '105', '107', '111', '112', '113', '114', '116', '118', '120', '122', '123', '128', '129', '130', '131', '133', '136', '139', '141', '142', '147', '148', '149', '152', '153', '154', '155', '156', '158', '159', '161', '162', '163', '164', '165', '167']
    t=[1,2,3,4,100,120]
    test = create_schedule(t)
    print(test)