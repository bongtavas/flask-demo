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