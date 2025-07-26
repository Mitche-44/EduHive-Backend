# Token management logic for flask_jwt_extended
# @jwt.token_in_blocklist_loader
# @jwt.additional_claims_loader
from extensions import jwt, blacklist
from models.user import User 

# blacklisting a user after logout

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in blacklist


#checks @jwt_required

@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    user = User.query.get(identity)
    return {
        "role": user.role,
        "email": user.email
    }
