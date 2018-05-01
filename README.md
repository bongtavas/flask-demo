## Setup

**Install virtualenv**

```bash
$ pip3 install virtualenv
```

**Create Directory twitter_api**
```bash
$ mkdir twitter_api
$ cd twitter_api
```

**Create and Start Virtual Environment**
```bash
$ virtualenv venv
$ source venv/bin/activate
```

**Install dependencies**

```bash
$ pip install flask
```

## Implementation
**Create the following files**

```
twitter_api
|--- __init__.py
|--- db.py
|--- schema.sql
|--- users.py
|--- tweets.py
```

**Define our database schema in schema.sql**
```sql
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS tweets;


CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL
);

CREATE TABLE tweets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tweet_body TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users (id)
);
```

**Paste the following database connection boilerplate in db.py.**

```python
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
```

In __init__.py, we define our Flask app. We then initialize our database with the flask app instance. 
```python
import os

from flask import Flask
from twitter_api import db, tweets, users

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'twitter-api.sqlite'),
    )

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    db.init_app(app)

    return app
```

**In users.py, we create our /users blueprint. Blueprints makes it easy to attach routes to our Flask app.**

```python
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
```

**In tweets.py, we define our /tweets blueprint**

```python
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
```


**We then add our blueprints in our flask app in __init__.py**
```
import os

from flask import Flask
from twitter_api import db, tweets, users

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'twitter-api.sqlite'),
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    db.init_app(app)
    app.register_blueprint(users.bp)
    app.register_blueprint(tweets.bp)

    return app
```

**Run our Flask server to test**
```
export FLASK_APP = twitter_api
export FLASK_ENV = development
flask run
```
