import os
from flask import Blueprint, render_template
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, validators
import sys
sys.path.append("..")
from modules.login_manager import loginManager
from models import db

frontend = Blueprint('frontend', __name__,
        template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))

class LoginForm(Form):
  username = TextField('Username', [validators.Required()])
  password = PasswordField('Password', [validators.Required()])

  def __init__(self, *args, **kwargs):
      Form.__init__(self, *args, **kwargs)
      self.user = None

  def validate(self):
    rv = Form.validate(self)
    if not rv:
      return False

    user = db.User.query.filter_by(
        name=self.email_address.data).first()
    if user is None:
      self.name.errors.append('Unknown username')
      return False

    if not user.check_password(self.password.data):
      self.password.errors.append('Invalid password')
      return False

    self.user = user
    return True

@frontend.route('', methods=['GET'])
def test_page():
    return render_template('test.html')

@frontend.route("login", methods=["GET", "POST"])
def login():
  form = LoginForm()
  if form.validate_on_submit():
    # login and validate the user...
    login_user(user)
    flash("Logged in successfully.")
    return redirect(request.args.get("next") or url_for("index"))
  return render_template("login.html", form=form)


@frontend.route('createDonor', methods=['GET'])
@login_required
def donor_creation_page():
    return render_template('DonorCreation.html')

@login_required
@frontend.route('donate', methods=['GET'])
def donation_form_page():
    return render_template('DonationForm.html')

