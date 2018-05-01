import functools

from flask import (
    Blueprint, jsonify, request
)

from twitter_api.db import get_db

bp = Blueprint('tweets', __name__, url_prefix='/tweets')

@bp.route ('/', methods=('GET', 'POST'))
def index():
    db = get_db()
    if request.method == 'GET':
        tweets = retrieve_tweets(db)
        return jsonify(tweets)

    elif request.method == 'POST':

        created_tweet = create_tweet(db)
        return jsonify(created_tweet) 

def retrieve_tweets(db):
    tweet_rows = db.execute('SELECT t.id, tweet_body, user_id, username FROM tweets t JOIN users u ON t.user_id = u.id').fetchall()
    tweets = [tweet_serializer(tweet_row) for tweet_row in tweet_rows]

    return tweets

def create_tweet(db):
    # Get parameters from POST body
    tweet_body = request.form['tweet_body']
    user_id = request.form['user_id']

    # Insert parameters into database
    cursor = db.execute('INSERT INTO tweets (tweet_body, user_id) VALUES (?, ?)', (tweet_body, user_id))
    db.commit()
    
    # Fetch latest insert, so we can use it as a response
    tweet_row = db.execute('SELECT t.id, tweet_body, user_id, username' 
    ' FROM tweets t JOIN users u ON t.user_id = u.id' 
    ' WHERE t.id = ?', (cursor.lastrowid, )).fetchone() 
    
    return tweet_serializer(tweet_row)

def tweet_serializer(tweet_row):
    return {
        'id' : tweet_row['id'],
        'tweet_body': tweet_row['tweet_body'],
        'user_id' : tweet_row['user_id'],
        'username' : tweet_row['username'],
    }