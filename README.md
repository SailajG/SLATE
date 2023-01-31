# SLATE - Hustle Free Meetings ! 
  ### Connect your availability Calendar with your friends.

# Contents

* [About](#about)
* [Installation](#installation)
* [Setup](#setup)
* [Architecture](#architecture)
* [Front End](#front-end)
* [Backend](#backend)
* [Rest APIs](#rest-apis)
* [Rest External API](#rest-external-api)
* [Disclaimer](#disclaimer)


# About
SLATE is an amazing Calender App by which we can share our calendars with friends and plan meetings with them accordingly , Great app for keep up balance with friends and our own meetings. This Application just uses our google calender API , Once the user logged in with email ID , the user is directed to calender page where the user can provide the user's availability for the current week and also for the future weeks. These availability created are also visible to the users friends by which they can plan accordingly to each others availability.

# Installation
Guide to set the environment
- [Git](https://git-scm.com/downloads) or other git environment
- [Python 3](https://www.python.org/downloads/) 
  Ensure that `python` is at least v3.0.
- [pip](https://pypi.org/project/pip/)

# Setup
To run this project, install it locally:
```
$ git clone https://github.com/sankariraja25/slate.git
$ pip install -r requirements.txt
$ python app.py
```
Launch `http://127.0.0.1:5000/`

# Depolyment
- Creating docker application of the image.
- Push the docker image to gcr.io registry.
- Deployment of application in GKE cluster.
- Creating horizontal pod scaling for the application.

# Architecture
<img width="655" alt="Screenshot 2022-04-11 at 9 14 24 am" src="https://user-images.githubusercontent.com/33536687/162698463-587d6c9f-b42a-4150-b6ff-d9c219d4c5d3.png">


# Front End
<img width="1434" alt="Screenshot 2022-04-11 at 9 14 01 am" src="https://user-images.githubusercontent.com/33536687/162694034-5ef1a5fe-63f7-4524-9c0f-1de4b76fc0e1.png"><img width="1388" alt="Screenshot 2022-04-11 at 1 47 28 am" src="https://user-images.githubusercontent.com/33536687/162700752-59410e78-500f-44a2-9d65-0fae0b1c77b8.png">

# Backend
- [MySQL](https://www.mysql.com/) to manage database locally
- [Google Cloud SQL](https://cloud.google.com/products/databases) managed `cloud database` service to run MySQL

# Rest APIs

App routes are used to interact with the REST service

- `/login` uses google oAuth to login the user and insert a row for the users into user table if there is not currently a row.
- `/schedule` shows the logged-in user's schedule for the week
- A different week can be shown using `/schedule/date=<start_date>`
- A different user's e.g. a friend's schedule can be viewed using `/schedule/user=<user_id>`

# Rest External API

[Google Calendar API](https://developers.google.com/calendar/api/guides/overview) The Google Calendar API is a RESTful API that can be accessed through explicit HTTP calls or via the Google Client Libraries. The API exposes most of the features available in the Google Calendar Web interface.




# Disclaimer

This project is part of a cloud computing coursework taught by [Dr. Sukhpal Singh Gill](https://github.com/iamssgill) at the Queen Mary University of London Electrical Engineering & Computer Science Department to create a prototype of a cloud application.

Check our app demonstration on YouTube by clicking here [https://www.youtube.com/watch?v=8V8viTkikx8](https://www.youtube.com/watch?v=8V8viTkikx8)

    


