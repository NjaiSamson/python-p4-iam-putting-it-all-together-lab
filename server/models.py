from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from config import db, bcrypt
from sqlalchemy.exc import IntegrityError

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    serialize_rules = ('-recipes.user', '-_password_hash',)

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    _password_hash = Column(String)
    image_url = Column(String)
    bio = Column(String)

    recipes = relationship('Recipe', back_populates='user', cascade='all, delete-orphan')

    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hashes may not be viewed.")

    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))

    def __repr__(self):
        return f'<User {self.username}, {self.bio}>'


class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    
    serialize_rules = ('-user.recipes',)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String, nullable=False)
    instructions = Column(String, nullable=False)
    minutes_to_complete = Column(Integer)

    user = relationship('User', back_populates='recipes')

    @validates('instructions')
    def validates_instructions(self, key, instruction):
        if len(instruction) < 50:
            raise ValueError("The instructions should be at least 50 characters long.")
        return instruction

    def __repr__(self):
        return f'<Recipe {self.title}, {self.instructions}>'
