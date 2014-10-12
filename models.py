from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Donor(db.Model):
    __tablename__ =  'donor'
    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String(80), unique=True)
    name = db.Column(db.String(80))
    contact_number = db.Column(db.String(20))
    address = db.Column(db.String(160))
    donations = db.relationship('Donation', backref='donor', lazy='dynamic')

    def __init__(self, email_address, name='', contact_number='', address=''):
        self.email_address = email_address
        self.name = name
        self.contact_number = contact_number
        self.address = address

class User(db.Model):
  __tablename__ =  'user'
  """The internal user who wants to login"""
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80))
  password = db.Column(db.String(80))

  def __init__(self, name, password):
    self.name = name
    self.password = password

  def is_active(self):
    return True

  def is_authenticated(self):
    return True

  def get_id(self):
    return self.name
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
    date = db.Column(db.String(20))
    amount = db.Column(db.Integer)
    mode = db.Column(db.String(20))
    cheque_number = db.Column(db.String(20))
    cheque_date = db.Column(db.String(20))
    transcation_id = db.Column(db.String(20))

    def __init__(self, date, amount, mode, cheque_number='', cheque_date='', transcation_id=''):
        self.date = date
        self.amount = amount
        self.mode = mode
        self.cheque_number = cheque_number
        self.cheque_date = cheque_date
        self.transcation_id = transcation_id
