import unittest
from flask_testing import TestCase  
from app import *

class BankingAPITestCase(TestCase):
    def create_app(self):
        # Set up the Flask app for testing
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  
        return app

    def setUp(self):
        # Set up the database before each test
        with app.app_context():
            db.create_all()

    def tearDown(self):
        # Drop all tables after each test
        with app.app_context():
            db.drop_all()

    def test_create_account(self):
        # Test POST /accounts (create account)
        response = self.client.post('/accounts', json={
            'name': 'Test User',
            'email': 'testuser@gmail.com',
            'balance': 500.00,
            'type': 'savings'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('Account created successfully', response.get_json()['message'])

    def test_create_account_missing_type(self):
        # Test for missing account type
        response = self.client.post('/accounts', json={
            'name': 'Test User',
            'email': 'testuser@gmail.com',
            'balance': 500.00
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('account type must be specified', response.get_json()['error'])

    def test_deposit_transaction(self):
        # Test POST /transactions/deposit
        account_response = self.client.post('/accounts', json={
            'name': 'Deposit User',
            'email': 'deposituser@gmail.com',
            'balance': 100.00,
            'type': 'savings'
        })
        account_id = account_response.get_json()['account_id']

        deposit_response = self.client.post('/transactions/deposit', json={
            'id': account_id,
            'amount': 200.00
        })
        self.assertEqual(deposit_response.status_code, 200)
        self.assertIn('Deposit successful', deposit_response.get_json()['message'])

    def test_withdraw_transaction(self):
        # Test POST /transactions/withdraw
        account_response = self.client.post('/accounts', json={
            'name': 'Withdraw User',
            'email': 'withdrawuser@gmail.com',
            'balance': 500.00,
            'type': 'current'
        })
        account_id = account_response.get_json()['account_id']

        withdraw_response = self.client.post('/transactions/withdraw', json={
            'id': account_id,
            'amount': 300.00
        })
        self.assertEqual(withdraw_response.status_code, 200)
        self.assertIn('Withdrawal successful', withdraw_response.get_json()['message'])

    def test_withdraw_insufficient_balance(self):
            # Test withdraw with insufficient balance
            account_response = self.client.post('/accounts', json={
                'name': 'Insufficient User',
                'email': 'insufficientuser@gmail.com',
                'balance': 100.00,
                'type': 'savings'
            })
            account_id = account_response.get_json()['account_id']

            withdraw_response = self.client.post('/transactions/withdraw', json={
                'id': account_id,
                'amount': 150.00
            })
            self.assertEqual(withdraw_response.status_code, 400)
            self.assertIn('Insufficient balance', withdraw_response.get_json()['error'])

  
if __name__ == '__main__':
    unittest.main()

if __name__ == '__main__':
    unittest.main()