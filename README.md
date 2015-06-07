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
- Using sqlalchemy for database
- Using httpauth for authenticate
- Using passlib for safer hash password

Installation
------------

First you must install virtualenv and flask to run flask apps.
See http://flask.pocoo.org/docs/0.10/installation/

Also you have to install dependency libraries, `flask-sqlalchemy`, `flask-httpauth`, and `passlib`

Run the web service:

    $ python ./app.py

Curl Usage
----------

Register:

    $ curl -i -X POST -H "Content-Type: application/json" -d '{"username":"ujang","password":"python"}' http://127.0.0.1:5000/api/users

Post a tweet:

    $ curl -u ujang:python -i -X POST -H "Content-Type: application/json" -d '{"tweet":"ini tweet pertamaku"}' http://127.0.0.1:5000/api/tweet

Get all tweet:

    $ curl -i -X GET -H "Content-Type: application/json" http://127.0.0.1:5000/api/tweet

Search tweets:

    $ curl -i -X POST -H "Content-Type: application/json" http://127.0.0.1:5000/api/search/q=perta

Get tweet by id:

    $ curl -i -X GET -H "Content-Type: application/json" http://127.0.0.1:5000/api/tweet/1

Edit tweet:

    $ curl -u ujang:python -i -X PATCH -H "Content-Type: application/json" -d '{"tweet":"tweet ini sudah disunting"}' http://127.0.0.1:5000/api/tweet/1

Delete tweet:

    $ curl -u ujang:python -i -X DELETE -H "Content-Type: application/json" http://127.0.0.1:5000/api/tweet/1
