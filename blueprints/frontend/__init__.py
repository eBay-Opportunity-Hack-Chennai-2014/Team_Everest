import os

from flask import Blueprint, render_template

from models import Donor

frontend = Blueprint('frontend', __name__,
        template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))

@frontend.route('', methods=['GET'])
def test_page():
    return render_template('test.html')
    
@frontend.route('login', methods=['GET'])
def login_page():
    return render_template('Login.html')
    
@frontend.route('createDonor', methods=['GET'])
def donor_creation_page():
    return render_template('DonorCreation.html')
    
@frontend.route('donate', methods=['GET'])
def donation_form_page():
    return render_template('DonationForm.html', donors = Donor.query.all())

@frontend.route('donations', methods=['GET'])
def view_donations():
    return render_template('view_donations.htm')
