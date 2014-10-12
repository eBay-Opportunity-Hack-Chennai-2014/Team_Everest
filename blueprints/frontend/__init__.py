import os
from flask import Blueprint, render_template, flash, redirect, request,url_for
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, validators
import sys
sys.path.append("..")
from modules.login_manager import loginManager
from models import db, Donor, Donation

frontend = Blueprint('frontend', __name__,
        template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))

@loginManager.user_loader
def load_user(userid):
  print 'Load user being done '
  return User.query.filter_by(name=userid).first()

@frontend.route('', methods=['GET'])
def test_page():
  return render_template('test.html')

# @frontend.route('registerNew', methods = ["POST"])
# def create_user():
#   user = User("user@everest.com","pass123")
#   db.session.add(user)
#   db.session.commit()

@frontend.route('donate', methods=['GET'])
def donation_form_page():
    return render_template('DonationForm.html', donors=Donor.query.all())

@frontend.route("login", methods=["GET", "POST"])
def login():
  form = request.form
  print "\n\n\n\n"
  print request.method
  if request.method == 'POST':
    print "Validation\n\n\n\n"

    donor = Donor.query.filter_by(email = form['email'])
    print form['email']
    print form['password']


    # login and validate the user...


    # login_user("Donor object")
    flash("Logged in successfully.")
    # print "hi"+type(url_for(".donor_form_page"))
    return redirect(request.args.get("next") or url_for("frontend.donation_form_page"))
  return render_template("Login.html", form=form)

@frontend.route('createDonor', methods=['GET'])
def donor_creation_page():
    return render_template('DonorCreation.html')

@frontend.route('donations', methods=['GET'])
@login_required
def view_donations():
    return render_template('view_donations.htm', donations=Donation.query.all())
