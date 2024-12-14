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

#Define route for the home page
@app.route('/')  
def home():
    return 'Welcome to the Banking API!'

#Define route to create the database
@app.route('/create-db')
def create_db():
    try:
        with app.app_context():
            db.create_all()
            return 'Database created successfully'
    except Exception as e:
            return f'Failed to create database: {e}'

#Define route to add sample data for testing
@app.route('/add-sample-data')
def add_sample_data():
    try:
        existing_account = Account.query.filter_by(email='tadiwa7@gmail.com').first()
        if existing_account:
            db.session.delete(existing_account)
            db.session.commit()

        account = Account(name='Tadiwa', email='tadiwa7@gmail.com', balance=1000.00, account_type='savings')
        db.session.add(account)
        db.session.commit()
        return 'Sample account added successfully'
    
    except Exception as e:
        db.session.rollback()
        return f"Error occurred: {str(e)}"

#Define route to view all accounts
@app.route('/accounts', methods=['GET'])
def view_accounts():
    try:
        accounts = Account.query.all()
        account_list = []
        for account in accounts:
            account_list.append({
                'id': account.id,
                'name': account.name,
                'email': account.email,
                'balance': account.balance
            })
        return {'accounts': account_list}
    
    except Exception as e:
        return {'error': f'An error occurred while fetching accounts: {str(e)}'}, 500

# Define route to create account
@app.route('/accounts', methods=['POST'])
def create_account():
    data = request.get_json()
    if not data:
        return {'error': 'No data provided in the request body'}, 400
    
    name = data.get('name')
    email = data.get('email')
    balance = data.get('balance', 0.0)
    account_type = data.get('account_type')

    if not name or not email:
        return {'error': 'name and email must be provided'}, 400
    
    if not account_type:
        return {'error': 'account type must be specified'}, 400

    if Account.query.filter_by(email=email).first():
        return {'message': 'Account already exists'}, 400

    try :
        new_account = Account(name=name, email=email, balance=balance, account_type = account_type)
        db.session.add(new_account)
        db.session.commit()
        return {'message': 'Account created successfully', 'account_id': new_account.id}, 201
    
    except Exception as e:
        db.session.rollback()
        return {'error': 'An error occurred while creating the account', 'details': str(e)}, 500


if __name__ == '__main__':
    app.run(debug=True)