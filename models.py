from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from sqlalchemy.exc import SQLAlchemyError

#Create a Flask app
app = Flask(__name__)

#Configure the SQLAlchemy database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


#Create an instance of the SQLAlchemy database
db = SQLAlchemy(app)

#Define the Account model
class Account(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    balance = db.Column(db.Float, default=0.0)
    account_type = db.Column(Enum('savings', 'current', name='account_type'), nullable=False)


#Define the Transaction model
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(Enum('withdraw', 'deposit', name='transaction'), nullable=False)
    account = db.relationship('Account', backref='transactions')