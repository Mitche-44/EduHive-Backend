from extensions import jwt

@jwt.user_identity_loader
def user_identity_lookup(user):
    return {"id": user.id, "role": user.role}

# Now every time you do this:


# create_access_token(identity=user)
# …it will automatically embed both id and role.