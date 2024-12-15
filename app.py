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
    type = db.Column(Enum('savings', 'current', name='account_type'), nullable=False)

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

        account = Account(name='Tadiwa', email='tadiwa7@gmail.com', balance=1000.00, type='savings')
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
                'balance': account.balance,
                'type': account.type
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
    type = data.get('type')

    if not name or not email:
        return {'error': 'name and email must be provided'}, 400
    
    if not type:
        return {'error': 'account type must be specified'}, 400

    if Account.query.filter_by(email=email).first():
        return {'message': 'Account already exists'}, 400

    try :
        new_account = Account(name=name, email=email, balance=balance, type = type)
        db.session.add(new_account)
        db.session.commit()
        return {'message': 'Account created successfully', 'account_id': new_account.id}, 201
    
    except Exception as e:
        db.session.rollback()
        return {'error': 'An error occurred while creating the account', 'details': str(e)}, 500

#Define route to get account by ID
@app.route('/accounts/<int:id>', methods=['GET'])
def get_account(id):

    account = Account.query.get(id)
    if not account:
        return {'error': 'Account not found'}, 404

    return {
        'id': account.id,
        'name': account.name,
        'email': account.email,
        'balance': account.balance,
        'type': account.type
    }

#Define route to update an existing account by ID
@app.route('/accounts/<int:id>', methods=['PUT'])
def update_account(id):

    data = request.get_json()
    if not data:
        return {'error': 'No data provided for update'}, 400
    
    account = Account.query.get(id)
    if not account:
        return {'error': 'Account not found'}, 404
    
    name = data.get('name')
    email = data.get('email')
    balance = data.get('balance')
    type = data.get('type')
    
    if email and Account.query.filter(Account.email == email, Account.id != id).first():
        return {'error': 'Email already in use by another account'}, 400

    if balance is not None:
        try:
            balance = float(balance)
            if balance < 0:
                return {'error': 'Balance cannot be negative'}, 400
        except ValueError:
            return {'error': 'Invalid balance value'}, 400

    if type and type not in ['savings', 'current']:
        return {'error': 'Invalid account type. Must be "savings" or "current"'}, 400
    
    if name:
        account.name = name
    if email :
        account.email = email
    if balance is not None:
        account.balance = balance
    if type:
        account.type = type

    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return {'error': 'Database error: ' + str(e)}, 500
    
    return {'message': 'Account updated successfully'}, 200

#Define route for deposit transaction
@app.route('/transactions/deposit', methods=['POST'])
def deposit():

    data = request.get_json()
    if not data:
        return {'error': 'Request body is missing'}, 400

    account_id = data.get('id')
    amount = data.get('amount')

    if not account_id or not amount:
        return {'error': 'Account ID and amount are required'}, 400
    
    account = Account.query.get(account_id)
    if not account:
        return {'error': 'Account not found'}, 404
    
    if amount <= 0:
        return {'error': 'Amount must be greater than 0'}, 400

    try:
        account.balance += amount
        transaction = Transaction(account_id=account.id, amount=amount, type='deposit')
        db.session.add(transaction)
        db.session.commit()
    
    except Exception as e:
        db.session.rollback()
        return {'error': f'An error occurred while processing the deposit: {str(e)}'}, 500
    
    return {'message': 'Deposit successful', 'new balance': account.balance}

#Define route for withdrawl transaction
@app.route('/transactions/withdraw', methods=['POST'])
def withdrawl():

    data = request.get_json()
    if not data:
        return {'error': 'Request body is missing'}, 400
    
    account_id = data.get('id')
    amount = data.get('amount')

    if not account_id or amount is None:
        return {'error': 'Account ID and amount are required'}, 400
    
    account = Account.query.get(account_id)
    if not account:
        return {'error': 'Account not found'}, 404

    if amount <= 0:
        return {'error': 'Amount must be greater than zero'}, 400
    
    if amount > account.balance:
        return {'error': 'Insufficient balance'}, 400
    
    try:
        account.balance -= amount
        transaction = Transaction(account_id=account.id, amount=amount, type='withdraw')
        db.session.add(transaction)
        db.session.commit()
    
    except Exception as e:
        db.session.rollback()
        return {'error': f'An error occurred while processing the deposit: {str(e)}'}, 500
    
    return {'message': 'Withdrawal successful', 'new balance': account.balance}


# Define route to fetch transaction history of an account
@app.route('/accounts/<int:id>/transactions', methods=['GET'])
def get_transaction_history(id):
    account = Account.query.get(id)
    if not account:
        return {'error': 'Account not found'}, 404

    try:
        transactions = Transaction.query.filter_by(account_id=id).all()
        transaction_list = []
        for transaction in transactions:
            transaction_list.append({
                'id': transaction.id,
                'amount': transaction.amount,
                'type': transaction.type,
                'account_id': transaction.account_id
            })
        return {'account_id': id, 'transactions': transaction_list}, 200
    
    except Exception as e:
        return {'error': f'An error occurred while fetching transactions: {str(e)}'}, 500
    
if __name__ == '__main__':
    app.run(debug=True)