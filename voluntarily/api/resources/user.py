from datetime import datetime
import requests
import elasticsearch.exceptions

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required

from voluntarily.commons.serializers import UserSchema, UserListSchema, SearchSchema
from voluntarily.extensions import es, ma, geocoder
from voluntarily.commons.query_builder import build_query
from voluntarily.commons.errors import UserExists
from voluntarily.config import ELASTICSEARCH


class UserResource(Resource):
    """Single object resource

    ---
    get:
      tags:
        - api
      parameters:
        - in: path
          name: user_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  user: UserSchema
        404:
          description: user does not exists
    put:
      tags:
        - api
      parameters:
        - in: path
          name: user_id
          schema:
            type: integer
      requestBody:
        content:
          application/json:
            schema:
              UserSchema
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: user updated
                  user: UserSchema
        404:
          description: user does not exists
    post:
      tags:
        - api
      parameters:
        - in: path
          name: user_id
          schema:
            type: integer
      requestBody:
        content:
          application/json:
            schema:
              UserSchema
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: user updated
        404:
          description: user does not exists
    delete:
      tags:
        - api
      parameters:
        - in: path
          name: user_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: user deleted
        404:
          description: user does not exists
    """

    # method_decorators = [jwt_required]

    def get(self, user_id):
        user = es.get(
            index=ELASTICSEARCH["user_index"],
            id=user_id
        )['_source']
        return {"user": UserSchema().dump(user)}


    def put(self, user_id):
        body = request.json
        user = es.index(
            index=ELASTICSEARCH["user_index"],
            body=request.json
        )
        return {"msg": "user updated"}


    def delete(self, user_id):
        user = es.get(
            index=ELASTICSEARCH["user_index"],
            id=user_id
        )['_source']
        user['active'] = False
        es.index(
            index=ELASTICSEARCH["user_index"],
            id=user_id,
            body=user
        )
        return {"msg": "user deleted"}

    def post(self, user_id):
        body = request.json
        if (es.exists(index=ELASTICSEARCH["user_index"], id=user_id)):
            raise UserExists()
        body["lastUpdated"] = datetime.now()
        body["createdAt"] = datetime.now()
        user_input_address = body.get("location", {}).get("userInput")
        if user_input_address:
            geocode_result =  geocoder.geocode_raw_input(user_input_address)
            body["location"] = geocode_result
        user = es.index(
            index=ELASTICSEARCH["user_index"],
            id=user_id,
            body=body
        )
        return {"msg": "user created"}


class UserList(Resource):
    """Search
    ---
    post:
      tags:
        - api
      requestBody:
        content:
          application/json:
            schema:
              SearchSchema
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: user created
                  users: UserListSchema
    """
    def post(self):
        """Paginate over all users
        """
        body = request.json
        query = build_query(body)
        results = es.search(
            index=ELASTICSEARCH["user_index"],
            body=query
        )
        o = {
            "users": [x["_source"] for x in results["hits"]["hits"]]
        }
        return UserListSchema().dump(o)