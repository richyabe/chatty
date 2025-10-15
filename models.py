from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(200), unique=True, index=True)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(200))
    created = db.Column(db.DateTime, default=datetime.now)

    # One-to-Many relationship with Blog
    blogs = db.relationship('Blog', back_populates='user', cascade="all, delete")

    def __repr__(self):
        return "<User {}>".format(self.username)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_published = db.Column(db.DateTime, default=datetime.now, nullable=False)

    # Foreign key relationship with User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_blog_user'), nullable=False)

    
    # One-to-Many relationship with User
    user = db.relationship('User', back_populates='blogs')

    def __repr__(self):
        return "<Blog {}>".format(self.title)
