#!flask/bin/python

import os, json
from datetime import datetime
from flask import Flask, abort, request, jsonify, g, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context

# initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

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
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.query.filter_by(username=username_or_token).first()
    if not user or not user.verify_password(password):
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
        abort(400)    # existing user
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({'username': user.username}), 201,
            {'Location': url_for('get_user', id=user.id, _external=True)})

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

@app.route('/api/tweet/search/q=<query>', methods=['GET'])
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
    return (jsonify({'tweet': tw}), 201,
            {'Location': url_for('get_tweet', id=tweet.id, _external=True)})

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
