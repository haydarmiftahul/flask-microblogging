Flask-Microblogging-Web-Service
===============================

Flask-Microblogging-Web-Service is web service based on Flask that allows you to interact with microblogging server. On the client site, it is preferred to run with curl.

Flask-Microblogging-Web-Service goal to make web service for microblogging.

Features
--------

- Basic support of RESTful APIs
- Register
- Authentication (by password per request or by token which will get session)
- Post tweet
- Get all tweet
- Search tweets
- Get tweet by id
- Edit tweet
- Delete tweet
- Using SQLAlchemy for database
- Using HTTPAauth for authenticate
- Using passlib for safer hash password
- Using itsdangerous for token

Installation
------------

- Install Python 2.7 and git.
- Run `setup.sh` (Linux, OS X, Cygwin) or `setup.bat` (Windows)
- Run `./app.py` to start the server (on Windows use `flask\Scripts\python app.py` instead)

Curl Usage
----------

Get all tweets:

    $ curl -i -X GET http://127.0.0.1:5000/api/tweet

Search tweets:

    $ curl -i -X GET http://127.0.0.1:5000/api/search/foo
    
Get tweet by id:

    $ curl -i -X GET http://127.0.0.1:5000/api/tweet/1

Register:

    $ curl -i -X POST -H "Content-Type: application/json" -d '{"username":"john","password":"doe"}' http://127.0.0.1:5000/api/users
    
Login:

    $ curl -u john:doe -i -X POST http://127.0.0.1:5000/api/login
    
Login will return JSON {"duration": 600, "token": "`foo`"}
`foo` used by below methods within the duration (600 second)
    
Logout:

    $ curl -i -X POST -H "X-CSRF-Token: foo" http://127.0.0.1:5000/api/logout

Post a tweet:

    $ curl -i -X POST -H "X-CSRF-Token: foo" -H "Content-Type: application/json" -d '{"tweet":"bar and baz"}' http://127.0.0.1:5000/api/tweet

Edit tweet:

    $ curl -i -X PATCH -H "X-CSRF-Token: foo" -H "Content-Type: application/json" -d '{"tweet":"baz run over the qux"}' http://127.0.0.1:5000/api/tweet/1

Delete tweet:

    $ curl -i -X DELETE -H "X-CSRF-Token: foo" http://127.0.0.1:5000/api/tweet/1
