from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required

from voluntarily.commons.serializers import SearchSchema, UserSchema
from voluntarily.commons.query_builder import build_query
from voluntarily.extensions import es
from voluntarily.config import ELASTICSEARCH


class MatchList(Resource):
    """Creation and get_all

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
                            user: UserSchema
    """
    # method_decorators = [jwt_required]

    def post(self):
        """On the fly matching

        TODO: Figure out highlighting
        {
            "user_id": 100,
            "distance": "10mi"
        }
        """
        body = request.json
        if "userId" in body:
            body = es.get(
                index=ELASTICSEARCH["user_index"],
                id=body["userId"]
            )['_source']
        query = build_query(body)
        result = es.search(index=ELASTICSEARCH["need_index"], body=query)
        return result