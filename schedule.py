import datetime as dt

from flask import render_template

class Schedule:
    def __init__(self, userId, requestStart, requestUserId):
        self.format = "%Y-%m-%d"
        self.currentWeekMinTime = dt.datetime.combine(dt.datetime.today() - dt.timedelta(days = dt.datetime.today().weekday()),dt.time.min)
        self.startDate = self.currentWeekMinTime.strftime(self.format)
        #Get start datetime from url date
        if requestStart != None:
            self.minTime = dt.datetime.combine(dt.datetime.strptime(requestStart, self.format).date(), dt.time.min)
        #Get start datetime from today's date
        else:
            self.minTime = self.currentWeekMinTime
        
        self.maxTime = self.minTime + dt.timedelta(days = 7) #Get datetime of end of week

        self.userId = userId
        self.requestUserId = requestUserId
        
    @staticmethod
    def get(self, conn):
        """
            Checks if a schedule exists for the user and week in the database.
            Returns HTTP status code 200 if it does and 404 if it does not.
        """
        cursor = conn.cursor()
        sql = "SELECT * FROM free_time WHERE user_id = %s AND week_start_date = %s"
        data = (self.userId, self.startDate)
        cursor.execute(sql, data)
        schedule = cursor.fetchone()
        print(schedule)
        if not schedule:
            return False
        else:
            return True

    def title(self):
        title = ""

        if self.requestUserId != None:
            #Need to set name to requestUser's name in the database
            name = str(self.requestUserId) 

            title += name + "'s "
        else:
            
            title += "MY"
  
        title += " FREE TIME"


        #Check if schedule is for current week
        if self.currentWeekMinTime == self.minTime:
            title += " FOR CURRENT WEEK"
        else:
            title += " FOR WEEK COMMENCING " + self.minTime.strftime("%a %d %b")
        
        return title
    
    def prev_week(self):
        self.startDate = (self.minTime - dt.timedelta(days = 7)).strftime(self.format)
        return self.startDate
    
    def next_week(self):
        self.startDate = (self.minTime + dt.timedelta(days = 7)).strftime(self.format)
        return self.startDate

    def get_events(self, events=[]):
        test_calendar_body = ""
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            test_calendar_body += start
            test_calendar_body += event['summary']
        return test_calendar_body


    def create_schedule(self, times=[], conn="" ):
        """Outputs a schedule for the week. Times the user is free are checked.

        Input parameters:
        times list -- array of id's corresponding to 1 hour slots where the user is free. If empty, checkboxes are unchecked.

        Returns:
        str -- HTML string of table
        """
        url_end = "/user="+str(self.userId)+"/date="+str(self.minTime.strftime(self.format))+""
        if self.get(self, conn):
            submit_url = "/schedule/update" + url_end
            submit_name = "Update" 
        else:
            submit_url = "/schedule/add" + url_end
            submit_name = "Insert" 


        

        htmlArray = [ "<form action='" + submit_url + "' method='POST'> <table><thead><tr><th>Time</th><th>Mon</th><th>Tues</th><th>Wed</th><th>Thur</th><th>Fri</th><th>Sat</th><th>Sun</th></thead><tbody>"]

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

        htmlArray.append("</tr></tbody></table> <input type='submit' value='"+submit_name+"'> </form>")
        print("test:", self.userId)
        delete_url = "/schedule/delete" + url_end
        print(delete_url)
        htmlArray.append("<a href= '"+delete_url+"'> Delete </a>")

        html = ' '.join(htmlArray)
         
        return html