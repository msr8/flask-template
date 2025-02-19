from app.extensions import db
# https://www.digitalocean.com/community/tutorials/how-to-use-one-to-many-database-relationships-with-flask-sqlalchemy




class User(db.Model):
    __tablename__ = 'users'

    email     = db.Column(db.String(255), primary_key=True)
    username  = db.Column(db.String(255), nullable=False)
    password  = db.Column(db.String(60),  nullable=True) # Bcrypt "blowfish algo" salted hash (by default it is 60 characters long)
    signed_up = db.Column(db.DateTime,    nullable=False, server_default=db.func.now())


    def __repr__(self):
        return f"User('{self.email}')"




class Usernames(db.Model):
    '''Exists only for O(1) lookup of usernames'''
    __tablename__ = 'usernames'

    username = db.Column(db.String(255), primary_key=True)
    email    = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"Usernames('{self.username}')"

