# UpdateMe [![Build Status](https://travis-ci.org/taliatrilling/UpdateMe.svg?branch=master)](https://travis-ci.org/taliatrilling/UpdateMe)

UpdateMe is a Twitter clone created by Talia Trilling for her Hackbright Academy Final Project. 
![UpdateMe Homepage](/static/images/homepage.png)

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
* Travis CI

(for specific dependencies, see requirements.txt)

## Instructions to Run UpdateMe Locally:

1. Navigate to the directory where you have cloned this repo, create a python virtual environment, and install the required dependencies:
`pip install -r requirements.txt`
2. Make sure that you have PostgreSQL installed, and then enter in your command line shell:
	* `createdb twitterclone`
	* `python model.py` 
3. If you would like to populate your application with fake users, you may take advantage of the fake_users.py file; run the program in an interactive python interpreter, run the command to connect to the database, and then populate your database as you wish with some of the built-in functions:
	* `python -i fake_users.py`
	* `connect_to_db(app)`
	* `add_users()`
	* `add_updates()`
	* `add_connections()`
4. Make sure to set your own secret key in the beginning of the server file, by changing the code in line 26 to:
```python
app.secret_key = "yoursecretkeyhere"
```
5. To begin running the application server, enter in your command line shell: 
	* `python server.py` 
6. Finally, navigate your browser to http://localhost:5000/

This app has been tested on a virtual machine running Ubuntu 16.04.1 LTS (GNU/Linux 4.4.0-31-generic x86_64)
