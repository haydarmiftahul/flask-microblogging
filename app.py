#!flask/bin/python

import os, json
from datetime import datetime
from flask import Flask, abort, request, jsonify, g, session
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

# initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ini ceritaku, mana ceritamu'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SERVER_NAME'] = '0.0.0.0:5000'

# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))
    tweets = db.relationship("Tweet", backref="user")

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)
    
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username
        }

    def generate_auth_token(self, expiration = 600):
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({ 'id': self.id })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            session.pop(User.query.get(data['id']))
            return None # valid token, but expired
        except BadSignature:
            session.pop(User.query.get(data['id']))
            return None # invalid token
        if data['id'] not in session:
            return None # user not logged in to session yet
        user = User.query.get(data['id'])
        return user

class Tweet(db.Model):
    __tablename__ = 'tweets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    tweet = db.Column(db.String(150))
    time = db.Column(db.DateTime(timezone=False))

    def serialize(self):
        return {
            'id': self.id,
            'tweet': self.tweet,
            'time': self.time.isoformat()
        }

@auth.verify_password
def verify_password(username, password):
    # first try to authenticate by token
    token = request.headers.get('X-CSRF-Token')
    if token is None:
        # try to authenticate with username
        user = User.query.filter_by(username=username).first()
        if not user or not user.verify_password(password):
            return False
    else:
        user = User.verify_auth_token(token)
        if user is None:
            return False
    g.user = user
    return True

@app.route('/api/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        return jsonify({'taken':username}), 400    # existing user
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'username': user.username}), 201

@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    if users is None:
        abort(400)
    us = []
    for u in users:
        us.append(u.serialize())
    us = json.dumps(us)
    return jsonify({'users': us})

@app.route('/api/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})

@app.route('/api/login', methods=['POST'])
@auth.login_required
def post_login():
    token = g.user.generate_auth_token(600) # login for 600 seconds
    session['id']=g.user.id
    return jsonify({'token': token.decode('ascii'), 'duration': 600})

@app.route('/api/logout', methods=['POST'])
@auth.login_required
def post_logout():
    session.pop(g.user.id)
    return jsonify({'logout':'OK'})

@app.route('/api/tweet/search/<query>', methods=['GET'])
def get_search(query):
    tweet = session.connection().execute(session.query(Tweet).filter(Tweet.tweet.op('(.*?)'+query+'(.*?)')(REGEX)))
    return jsonify({'tweets': tweet})

@app.route('/api/tweet', methods=['GET'])
def get_tweets():
    tweets = Tweet.query.all()
    tw = []
    for t in tweets:
        tw.append(t.serialize())
    tw = json.dumps(tw)
    return jsonify({'tweets': tw})

@app.route('/api/tweet/<int:id>', methods=['GET'])
def get_tweet(id):
    tweet = Tweet.query.get(id)
    if tweet is None:
        abort(404)    # tweet not found
    tweet = tweet.serialize()
    return jsonify({'tweet': tweet})

@app.route('/api/tweet', methods=['POST'])
@auth.login_required
def post_tweet():    
    tweet = request.json.get('tweet')
    time = datetime.now()
    if tweet is None:
        abort(400)    # missing arguments
    tw = Tweet(user_id=g.user.id,tweet=tweet,time=time)
    db.session.add(tw)
    db.session.commit()
    tw = tw.serialize()
    return jsonify({'tweet': tw}), 201

@app.route('/api/tweet/<int:id>', methods=['PATCH'])
@auth.login_required
def patch_tweet(id):
    tweet = request.json.get('tweet')
    if tweet is None:
        abort(400)    # missing arguments
    if Tweet.query.filter_by(id=id).first() is None:
        abort(400)    # no tweet found
    tw = Tweet.query.filter_by(id=id).first()
    if tw.user_id != g.user.id:
        abort(400)    # tweet not owned
    tw.tweet = tweet
    tw.time = datetime.now()
    db.session.commit()
    tw = tw.serialize()
    return jsonify({'tweet': tw})

@app.route('/api/tweet/<int:id>', methods=['DELETE'])
@auth.login_required
def delete_tweet(id):
    if Tweet.query.filter_by(id=id).first() is None:
        abort(400)    # no tweet found
    tw = Tweet.query.filter_by(id=id).first()
    if tw.user_id != g.user.id:
        abort(400)    # tweet not owned
    tweet = tw.tweet
    db.session.delete(tw)
    db.session.commit()
    return jsonify({'data': '\"%s\" deleted' % tweet})

if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        db.create_all()
    app.run(debug=True)
