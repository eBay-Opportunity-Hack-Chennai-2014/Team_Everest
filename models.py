from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Donor(db.Model):
    __tablename__ =  'donor'
    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String(80), unique=True)
    name = db.Column(db.String(80))
    address = db.Column(db.String(1000))
    contact_number = db.Column(db.String(20))
    donations = db.relationship('Donation', backref='donor', lazy='dynamic')

    def __init__(self, email_address, name, contact_number, address):
        self.email_address = email_address
        self.name = name
        self.contact_number = contact_number
        self.address = address

# class NGO(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email_address = db.Column(db.String(80), unique=True)
#     donations = db.relationship('Donation', backref='ngo', lazy='dynamic')
#
#     def __init__(self, email_address, name):
#         self.email_address = email_address
#         self.name = name

class Donation(db.Model):
    __tablename__ = 'donation'
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('donor.id'))
    date = db.Column(db.DateTime)
    amount = db.Column(db.Integer)
    mode = db.Column(db.String(20))
    mode_description = db.Column(db.String(200))

    def __init__(self, date, amount, mode, mode_description = ''):
        self.date = date
        self.amount = amount
        self.mode = mode
        self.mode_description = mode_description
