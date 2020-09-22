from flask import Blueprint
from flask_restx import Api
from flask_jwt_extended import JWTManager

from blacklist import BLACKLIST
from .category import api as category
from .brand import api as brand
from .item import api as item


jwt = JWTManager()

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',#'X-API-KEY',
        'description':'Please input Access token'
    }
}

blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(blueprint, doc='/documentation', title='Product management API', version='0.1', description='An API to manage product entry', authorizations=authorizations, security='apikey')

api.add_namespace(category)
api.add_namespace(brand)
api.add_namespace(item)

@jwt.user_claims_loader
# Remember identity is what we define when creating the access token
def add_claims_to_jwt(identity):
    if identity['privileges'] == 'Super Admin' or identity['privileges'] == 'Admin':  # instead of hard-coding, we should read from a file or database to get a list of admins instead
        return {"is_admin": True}
    return {"is_admin": False}

# This method will check if a token is blacklisted, and will be called automatically when blacklist is enabled
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    # Here we blacklist particular JWTs that have been created in the past.
    return (decrypted_token["jti"] in BLACKLIST)

# The following callbacks are used for customizing jwt response/error messages.
# The original ones may not be in a very pretty format (opinionated)
@jwt.expired_token_loader
def expired_token_callback():
    return {"message": "The token has expired.", "error": "token_expired"}, 401

@jwt.invalid_token_loader
# we have to keep the argument here, since it's passed in by the caller internally
def invalid_token_callback(error):
    return {"message": "Signature verification failed.", "error": "invalid_token"}, 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return {"description": "Request does not contain an access token.", "error": "authorization_required"}, 401

@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return {"description": "The token is not fresh.", "error": "fresh_token_required"}, 401

@jwt.revoked_token_loader
def revoked_token_callback():
    return {"description": "The token has been revoked.", "error": "token_revoked"}, 401
