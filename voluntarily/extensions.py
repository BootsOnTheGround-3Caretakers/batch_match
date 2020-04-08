"""Extensions registry

All extensions here are used as singletons and
initialized in application factory
"""
from elasticsearch import Elasticsearch
from passlib.context import CryptContext
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow


from voluntarily.commons.geocoder import Geocoder
from voluntarily.config import ELASTICSEARCH
from voluntarily.commons.apispec import APISpecExt

es = Elasticsearch()
ma = Marshmallow()
jwt = JWTManager()
apispec = APISpecExt()
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
geocoder = Geocoder(es)