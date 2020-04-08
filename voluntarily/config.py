"""Default configuration

Use env var to override
"""
import os

ENV = os.getenv("FLASK_ENV")
DEBUG = ENV == "development"
SECRET_KEY = os.getenv("SECRET_KEY")
HERE_CLIENT_ID = os.getenv('HERE_CLIENT_ID')
HERE_ACCESS_KEY_ID = os.getenv('HERE_ACCESS_KEY_ID')
HERE_ACCESS_KEY_SECRET = os.getenv('HERE_ACCESS_KEY_SECRET')

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
SQLALCHEMY_TRACK_MODIFICATIONS = False

JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]

ELASTICSEARCH = {
    "host": ["localhost"],
    "need_index": "needs",
    "user_index": "users"
}