from flask import Blueprint, current_app, jsonify
from flask_restful import Api
from marshmallow import ValidationError
import elasticsearch.exceptions

import voluntarily.commons.errors
from voluntarily.extensions import apispec
from voluntarily.api.resources import (
    UserList,
    UserResource,
    NeedList,
    NeedResource,
    MatchList
)
from voluntarily.commons.serializers import (
    UserSchema,
    UserListSchema,
    NeedSchema,
    SearchSchema
)


blueprint = Blueprint("api", __name__, url_prefix="/api/v1")
api = Api(blueprint, catch_all_404s=True)


api.add_resource(UserResource, "/user/<int:user_id>")
api.add_resource(UserList, "/users")
api.add_resource(NeedResource, "/need/<string:need_id>")
api.add_resource(NeedList, "/needs")
api.add_resource(MatchList, "/matches/<int:user_id>")


@blueprint.before_app_first_request
def register_views():
    apispec.spec.components.schema("UserSchema", schema=UserSchema)
    apispec.spec.components.schema("UserListSchema", schema=UserListSchema)
    apispec.spec.components.schema("NeedSchema", schema=NeedSchema)
    apispec.spec.components.schema("SearchSchema", schema=SearchSchema)
    apispec.spec.path(view=UserResource, app=current_app)
    apispec.spec.path(view=UserList, app=current_app)
    apispec.spec.path(view=NeedResource, app=current_app)
    apispec.spec.path(view=NeedList, app=current_app)


@blueprint.errorhandler(ValidationError)
def handle_marshmallow_error(e):
    """Return json error for marshmallow validation errors.

    This will avoid having to try/catch ValidationErrors in all endpoints, returning
    correct JSON response with associated HTTP 400 Status (https://tools.ietf.org/html/rfc7231#section-6.5.1)
    """
    return jsonify(e.messages), 400

@blueprint.errorhandler(elasticsearch.exceptions.ElasticsearchException)
def handle_elasticsearch_error(e):
    errors = {
        "NotFoundError": "the item does not exist",
        "ConnectionError": "no connection to the database",
        "RequestError": "there was an issue with the request",
        "ConflictError": "there was a conflict with the request"
    }
    elasticsearch_exception = type(e).__name__
    return {
        "msg": errors[elasticsearch_exception],
        "debug": {
            "info": e.info,
            "error": e.error
        }
    }, e.status_code

@blueprint.errorhandler(voluntarily.commons.errors.BatchMatchException)
def handle_batchmatch_error(e):
    return {
        "msg": e.message
    }, e.status
