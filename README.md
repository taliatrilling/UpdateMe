# UpdateMe [![Build Status](https://travis-ci.org/taliatrilling/UpdateMe.svg?branch=master)](https://travis-ci.org/taliatrilling/UpdateMe)

UpdateMe is a Twitter clone created by Talia Trilling for her Hackbright Academy Final Project. 

## Technology Stack:
* Python
* Flask 
* PostgreSQL
* SQLAlchemy
* Jinja2
* JavaScript/JQuery
* AJAX/JSON
* Bootstrap
* BCrypt/Passlib
* noty
* Faker/factory boy
* unittests


(for specific dependencies, see requirements.txt)

## Instructions to Run UpdateMe Locally:

1. Navigate to the directory where you have cloned this repo, create a python virtual environment, and install the required dependencies:
`pip install -r requirements.txt`
2. Make sure that you have PostgreSQL installed, and then enter in your command line shell:
`createdb twitterclone`

`python model.py` 
4. To begin running the application server, enter in your command line shell: 
`python server.py` 
5. Finally, navigate your browser to http://localhost:5000/

This app has been tested on a virtual machine running Ubuntu 16.04.1 LTS (GNU/Linux 4.4.0-31-generic x86_64)