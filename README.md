<img width="1440" alt="Screenshot 2022-04-10 at 7 59 19 PM" src="https://user-images.githubusercontent.com/98648659/162635361-c05d51de-60cd-4e07-8727-66bda7fd65cc.png">











# SLATE 
  #hustle free meetings 

# Contents

* About
* Architecture
* Front End
* Back End
* Web Server
* Running Locally
* Disclaimer



# About
SLATE is an amazing Calender App by which we can share our calendars with friends and plan meetings with them accordingly , Great app for keep up balance with friends and our own meetings. This Application just uses our google calender API , Once the user logged in with email ID , the user is directed to calender page where the user can provide the user's availability for the current week and also for the future weeks. These availability created are also visible to the users friends by which they can plan accordingly to each others availability.

# Architecture


# Front End

-Web front-end used so that any internet conencted device can access it.

-Currently the client web-application is hosted locally meaning the user needs to clone the github but in the future it is planned to host the web-application on google cloud.

App routes are used to interact with the REST service e.g. the following are for GET.

/login -> uses google oAuth to login the user and insert a row for the users into user table if there is not currently a row.

/schedule -> shows the logged-in user's schedule for the week

A different week can be shown using /schedule/date=<start_date> 

A different user's e.g. a friend's schedule can be viewed using /schedule/user=<user_id>

     





Getting started (after copying code to your computer):

1. Copy code to your computer

2. In terminal: pip install -r requirements.txt

3. From vscode terminal: python app.py

4. In browser go to: http://localhost:5000/


