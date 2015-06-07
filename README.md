Flask-Microblogging-Web-Service
===============================

Flask-Microblogging-Web-Service is web service based on Flask that allows you to interact with microblogging server. On the client site, it is preferred to run with curl.

Flask-Microblogging-Web-Service goal to make web service for microblogging.

Features
--------

- Basic support of RESTful APIs
- Register
- Authentication
- Post tweet
- Get all tweet
- Search tweets
- Get tweet by id
- Edit tweet
- Delete tweet
- Using SQLAlchemy for database
- Using HTTPAauth for authenticate
- Using passlib for safer hash password

Installation
------------

- Install Python 2.7 and git.
- Run `setup.sh` (Linux, OS X, Cygwin) or `setup.bat` (Windows)
- Run `./app.py` to start the server (on Windows use `flask\Scripts\python app.py` instead)

Curl Usage
----------


Register:

    $ curl -i -X POST -H "Content-Type: application/json" -d '{"username":"foo","password":"bar"}' http://127.0.0.1:5000/api/users

Post a tweet:

    $ curl -u ujang:python -i -X POST -H "Content-Type: application/json" -d '{"tweet":"foo and bar"}' http://127.0.0.1:5000/api/tweet

Get all tweets:

    $ curl -i -X GET -H "Content-Type: application/json" http://127.0.0.1:5000/api/tweet

Search tweets:

    $ curl -i -X POST -H "Content-Type: application/json" http://127.0.0.1:5000/api/search/q=foo
    
Get tweet by id:

    $ curl -i -X GET -H "Content-Type: application/json" http://127.0.0.1:5000/api/tweet/1

Edit tweet:

    $ curl -u ujang:python -i -X PATCH -H "Content-Type: application/json" -d '{"tweet":"bar run over the foo"}' http://127.0.0.1:5000/api/tweet/1

Delete tweet:

    $ curl -u ujang:python -i -X DELETE -H "Content-Type: application/json" http://127.0.0.1:5000/api/tweet/1
