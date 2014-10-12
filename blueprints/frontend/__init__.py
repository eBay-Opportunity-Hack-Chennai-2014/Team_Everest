import os
from flask import Blueprint, render_template, flash, redirect, request,url_for
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, validators
import sys
sys.path.append("..")
from modules.login_manager import loginManager
from models import db, Donor, Donation, User

frontend = Blueprint('frontend', __name__,
        template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))

@loginManager.user_loader
def load_user(userid):
  print 'Load user being done '
  return User.query.filter_by(name=userid).first()

class LoginForm(Form):
  name = TextField('Username', [validators.Required()])
  password = PasswordField('Password', [validators.Required()])
  def __init__(self, *args, **kwargs):
      Form.__init__(self, *args, **kwargs)
      self.user = None

  def validate(self):
    userObj =  User.query.all()[0]
    rv = Form.validate(self)
    if not rv:
      return False
    user = User.query.filter_by(
        name=self.name.data)

    if user is None:
      self.name.errors.append('Unknown username')
      return False

    user = User.query.filter_by(
        password=self.password.data)

    if user is None:
      self.password.errors.append('Invalid password')
      return False

    self.user = user.first()
    return True

@frontend.route('', methods=['GET'])
def test_page():
  return render_template('test.html')

@frontend.route('registerNew', methods = ["POST"])
def create_user():
  user = User("user@everest.com","pass123")
  db.session.add(user)
  db.session.commit()

@frontend.route('donate', methods=['GET'])
@login_required
def donation_form_page():
    return render_template('DonationForm.html', donors=Donor.query.all())

@frontend.route("login", methods=["GET", "POST"])
def login():
  form = LoginForm()
  print form.errors
  if form.validate_on_submit():
    # login and validate the user...
    login_user(form.user)
    flash("Logged in successfully.")
    # print "hi"+type(url_for(".donor_form_page"))
    # print request.args.get("next")
    return redirect(request.args.get("next") or url_for("frontend.donation_form_page"))
  return render_template("login.html", form=form)

@frontend.route('createDonor', methods=['GET'])
@login_required
def donor_creation_page():
    return render_template('DonorCreation.html')

@frontend.route('donations', methods=['GET'])
def view_donations():
    return render_template('view_donations.htm', donations=Donation.query.all())
