import json
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from extensions import db



class User(UserMixin, db.Model):
    __tablename__ = "users"
    

    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(), unique = True, nullable=False)
    password = db.Column(db.Text())
    roles = db.Column(db.String(50), nullable=False)
    
    name = db.Column(db.String(), nullable=True)
    lastname = db.Column(db.String(), nullable=True)
    cellphone = db.Column(db.String(), nullable=True)
    
    
    event_details = db.relationship('EventDetail', back_populates='user')
    
    
    
    def __init__(self, email, password, roles=["user"]):
        self.email = email
        self.roles = json.dumps(roles)
        
        self.password = generate_password_hash(password)
        
    def get_roles(self):
        return json.loads(self.roles)
    
    def __repr__(self):
        return f"<User {self.email}>"    
    

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
    @staticmethod
    def find_by_email(email):
        return User.query.filter_by(email=email).first()
