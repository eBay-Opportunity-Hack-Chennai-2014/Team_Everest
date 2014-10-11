from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Donor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String(80), unique=True)
    name = db.Column(db.String(80))
    contact_number = db.Column(db.String(20))
    donations = db.relationship('Donation', backref='donor', lazy='dynamic')

    def __init__(self, email_address, name, contact_number):
        self.email_address = email_address
        self.name = name
        self.contact_number = contact_number

# class NGO(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email_address = db.Column(db.String(80), unique=True)
#     donations = db.relationship('Donation', backref='ngo', lazy='dynamic')
#
#     def __init__(self, email_address, name):
#         self.email_address = email_address
#         self.name = name

class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('donor.id'))
    receipt_number = db.Column(db.String(20))
    date = db.Column(db.DateTime)
    amount = db.Column(db.Integer)
    mode = db.Column(db.String(20))
    cheque_date = db.Column(db.DateTime)
    cheque_number = db.Column(db.String(20))
    transaction_id = db.Column(db.String(20))

    def __init__(receipt_number, date, amount, mode, cheque_date='', cheque_number='', transaction_id = ''):
        self.receipt_number = receipt_number
        self.date = date
        self.amount = amount
        self.mode = mode
        self.mode_description = mode_description
        self.cheque_data = cheque_data
        self.cheque_number = cheque_number
        self.transaction_id = transaction_id
