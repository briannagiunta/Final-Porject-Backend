from sqlalchemy.sql.schema import Column
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    zip = db.Column(db.String)
    about = db.Column(db.String)
    image = db.Column(db.String)
    dogs = db.relationship('Dog', backref='user')
    potential_matches = db.relationship('Potential_match', backref='user')
    matches = db.relationship('Match', secondary='user_matches', backref='users')
    def to_json(self, dogs=False, matches=False):
        if dogs:
            return {
                "id": self.id,
                "name": self.name,
                "email": self.email,
                "zip": self.zip,
                "about": self.about,
                "image": self.image,
                "dogs": [d.to_json() for d in self.dogs]
            }
        elif matches:
            return {
                "id": self.id,
                "name": self.name,
                "email": self.email,
                "zip": self.zip,
                "about": self.about,
                "image": self.image,
                "matches": [m.to_json() for m in self.matches]
            }
        else:
            return {
                "id": self.id,
                "name": self.name,
                "email": self.email,
                "zip": self.zip,
                "about": self.about,
                "image": self.image,
                "potential_matches": [p.to_json() for p in self.potential_matches]
            }



class Dog(db.Model):
    __tablename__ = 'dogs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String)
    breed = db.Column(db.String)
    age = db.Column(db.Integer)
    size = db.Column(db.String)
    description = db.Column(db.String)
    image = db.Column(db.String)
    def to_json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "breed": self.breed,
            "age": self.age,
            "size": self.size,
            "description": self.description,
            "image": self.image 
        }

class Potential_match(db.Model):
    __tablename__ = 'potential_matches'
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user2_id = db.Column(db.Integer)
    def to_json(self):
        return{
            "id": self.id,
            "user1_id": self.user1_id,
            "user2_id": self.user2_id
        }


class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer)
    user2_id = db.Column(db.Integer)
    def to_json(self):
        return{
            "id": self.id,
            "user1_id": self.user1_id,
            "user2_id": self.user2_id
        }


class User_matches(db.Model):
    __tablename__ = 'user_matches'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'))
    def to_json(self):
        return{
            "id": self.id,
            "user_id": self.user_id,
            "match_id": self.match_id
        }
