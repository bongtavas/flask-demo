import functools

from flask import (
    Blueprint, flash, g, jsonify, request,
)

from twitter_api.db import get_db

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route ('/', methods=('GET', 'POST'))
def index():
    db = get_db()
    if request.method == 'GET':
        users = retrieve_users(db)
        return jsonify(users)

    elif request.method == 'POST':
        created_user = create_user(db)
        return jsonify(created_user)

def retrieve_users(db):
    # Fetch all users
    userRows = db.execute('SELECT id, username FROM users').fetchall()

    # Serialize Sqlite Rows to Dictionaries
    users = [ user_serializer(userRow) for userRow in userRows ]
    
    return users


def create_user(db):
    # Get parameters form POST body
    username = request.form['username']

    # Insert parameters to database
    cursor = db.execute('INSERT INTO users (username) VALUES (?)', (username, ))
    db.commit()

    # Fetch latest insert, so we can use it as a response
    userRow = db.execute('SELECT id, username FROM users WHERE id = ?', (cursor.lastrowid, )).fetchone() 
    
    return user_serializer(userRow)


def user_serializer(userRow):
    return {
        'id' : userRow['id'],
        'username':userRow['username']
    }