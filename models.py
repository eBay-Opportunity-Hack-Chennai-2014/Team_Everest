from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Donor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String(80))
    name = db.Column(db.String(80))
    contact_number = db.Column(db.String(20))
    donations = db.relationship('Donation', backref='donor', lazy='dynamic')

class NGO(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String(80))
    donations = db.relationship('Donation', backref='ngo', lazy='dynamic')

class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receipt_number = db.Column(db.String(20))
    date = db.Column(db.DateTime)
    amount = db.Column(db.Integer)
    mode = db.Column(db.String(20))
    mode_description = db.Column(db.String(80))
