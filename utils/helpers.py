# utils/helpers.py
# Utility functions for the EduHive application (email management, user creation)
def get_or_create_user(email, **kwargs):
    user = User.query.filter_by(email=email).first()
    if user:
        return user
    user = User(email=email, **kwargs)
    db.session.add(user)
    db.session.commit()
    return user
