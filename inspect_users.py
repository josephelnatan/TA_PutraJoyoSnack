from app import app, User

with app.app_context():
    users = User.query.all()
    if not users:
        print('NO_USERS')
    else:
        for user in users:
            print(f'{user.username}|{user.password}|{user.role}')
