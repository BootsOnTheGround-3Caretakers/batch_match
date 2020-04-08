from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required

from voluntarily.commons.serializers import NeedSchema, NeedListSchema, SearchSchema
from voluntarily.config import ELASTICSEARCH
from voluntarily.extensions import es
from voluntarily.commons.query_builder import build_query

# Watcher ID, array can be empty

class NeedResource(Resource):
    """Single object resource

    ---
    get:
      tags:
        - api
      parameters:
        - in: path
          name: need_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  need: NeedSchema
        404:
          description: need does not exists
    put:
      tags:
        - api
      parameters:
        - in: path
          name: need_id
          schema:
            type: integer
      requestBody:
        content:
          application/json:
            schema:
              NeedSchema
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: need updated
                  need: NeedSchema
        404:
          description: need does not exists
    post:
      tags:
        - api
      parameters:
        - in: path
          name: need_id
          schema:
            type: integer
      requestBody:
        content:
          application/json:
            schema:
              NeedSchema
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: need updated
        404:
          description: need does not exists
    delete:
      tags:
        - api
      parameters:
        - in: path
          name: need_id
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
                    example: need deleted
        404:
          description: need does not exists
    """

    # method_decorators = [jwt_required]

    def get(self, need_id):
        return es.get(
            index=ELASTICSEARCH["need_index"],
            id=need_id
        )['_source']


    def put(self, need_id):
        es.index(
            index=ELASTICSEARCH["need_index"],
            id=need_id,
            body=request.json
        )


    def delete(self, need_id):
        need = es.get(
            index=ELASTICSEARCH["need_index"],
            id=need_id
        )['_source']
        need['active'] = False
        es.index(
            index=ELASTICSEARCH["need_index"],
            id=need_id,
            body=need
        )

    def post(self):
        body = request.json
        need = es.index(
            index=ELASTICSEARCH["need_index"],
            body=request.json
        )


class NeedList(Resource):
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
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: user created
                  need: NeedListSchema
    """

    # method_decorators = [jwt_required]

    # search for need in geo
    # search for need in zip code
    # search for need by need_id -> get needs where need_id in matchedGiver
    # search for need by hashTag
    # search for need by needName
    def post(self):
        body = request.json
        query = build_query(body)
        results = es.search(
            index=ELASTICSEARCH["need_index"],
            body=query
        )
        o = {
            "needs": [x["_source"] for x in results["hits"]["hits"]]
        }
        return NeedListSchema().dump(o)