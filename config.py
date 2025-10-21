import os
import pathlib

class Config(object):
    # Use SECRET_KEY from environment, or fall back to a default one for local testing
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback_secret_key_123')

    # Database path (SQLite for local)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(pathlib.Path().absolute(), 'data.db')
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

