from __future__ import with_statement
import os
from flask import Blueprint, render_template, flash, redirect, request,url_for
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, validators
import sys
sys.path.append("..")
from modules.login_manager import loginManager
from models import db, Donor, Donation
import tempfile
from num2words import num2words
from xhtml2pdf import pisa
from werkzeug import secure_filename
from jinja2 import Template
import os
import datetime
import random
import StringIO
import xlrd

from contextlib import closing
from zipfile import ZipFile, ZIP_DEFLATED

from flask import Blueprint, render_template, session, request, make_response, send_file, abort,  current_app, redirect, url_for
from jinja2 import Template
from xhtml2pdf import pisa
from sqlalchemy.orm import sessionmaker
from models import db, Donor, Donation

from emailHelper import sendEmail

frontend = Blueprint('frontend', __name__,
        template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))

@loginManager.user_loader
def load_user(userid):
  print 'Load user being done '
  donor = Donor.query.filter_by(email_address=userid).first()
  print donor
  return donor

@frontend.route('donate', methods=['GET'])
def donation_form_page():
    return render_template('DonationForm.html', donors=Donor.query.all())

@frontend.route("login", methods=["GET", "POST"])
def login():
  form = request.form
  print request.method
  if request.method == 'POST':
    print "Validation\n\n\n\n"

    donor = Donor.query.filter_by(email_address = form['email']).first()
    # login and validate the user...
    login_user(donor)
    flash("Logged in successfully.")
    # print "hi"+type(url_for(".donor_form_page"))
    return redirect(request.args.get("next") or url_for("frontend.view_donations"))
  return render_template("Login.html")

@frontend.route('createDonor', methods=['GET'])
def donor_creation_page():
    return render_template('DonorCreation.html')

@frontend.route('donations', methods=['GET','POST'])
@login_required
def view_donations():
    #email = session.get('email')
    email = "Mr.X"
    if request.method == 'GET':
        donor = db.session.query.filter_by(email_address = email).first()
        if donor.is_admin:
            donations=Donation.query.all()
        else:
            donations = donor.donations
        return render_template('view_donations.htm', donations=donations)
    elif request.method == 'POST':
        donation_ids = request.form.keys()
        donor = db.session.query.filter_by(email_address = email).first()
        if donor.is_admin:
            donations=Donation.query.filter(Donation.id.in_(donation_ids)).all()
        else:
            donations = donor.donations
            donor_donation_ids = set(map(lambda x: x.id, donations))
            donor_accessible_donation_ids = []
            for i in donation_ids:
                if(i in donor_donation_ids):
                    donor_accessible_donation_ids.append(i)
            donation_ids = donor_accessible_donation_ids
            donations=Donation.query.filter(Donation.id.in_(donation_ids)).all()
            return generate_zipped_receipts(donations)

def generate_zipped_receipts(donations):
    pdfFiles = []
    for donation in donations:
        data = {'Amount':donation.amount, 'ReceiptNo':donation.id, 'DonationDate': donation.date, 'OrgName': "Team Everest", 'OrgAddress': "chennai", 'DonationMode': donation.mode, 'DonorName':donor.first().name, 'DonorAddress' : donor.first().address, 'Certification_Number' : "213213dsfdaf3", "WordAmount":num2words(donation.amount) }
        pdf = makePdf(data)
        pdfFiles.append(pdf)
    s = zipFiles(pdfFiles)
    response_body = open(s).read()
    os.remove(s)
    headers = {"Content-Disposition": "attachment; filename=receipt.zip"}
    return make_response((response_body,'200', headers))


"""take a list of file names and return a fd for the zipped file"""
def zipFiles(files):
    s = str(random.randint(0,10000000))
    s = "archivename"+s+".zip"
    z = ZipFile(s, "w", ZIP_DEFLATED)
    for f in files:
        z.write(f, f.split('/')[-1])
    z.close()
    return s

"""
gets data to be populated and creates the pdf
"""
def makePdf(data):
    if not data:
        raise Exception("null data in makeHtml");
    templateString = open("receipt_template.html").read()
    template = Template(templateString)
    html = template.render(data)
    return convertHtmlToPdf(html)

def convertHtmlToPdf(sourceHtml):
    resultFile = tempfile.NamedTemporaryFile(prefix='receipt_', suffix='.pdf', dir='/tmp', delete=False)
    # convert HTML to PDF
    pisaStatus = pisa.CreatePDF(
            sourceHtml,                # the HTML to convert
            dest=resultFile)           # file handle to recieve result
    return resultFile.name



