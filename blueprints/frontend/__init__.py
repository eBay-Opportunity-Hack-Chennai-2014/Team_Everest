from __future__ import with_statement
import os
from flask import Blueprint, render_template, flash, redirect, request,url_for
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, validators
import sys
from login_manager import lm
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

@lm.user_loader
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
    donor = Donor.query.filter_by(email_address = form['email']).first()
    # login and validate the user...
    if donor is None:
      return redirect(url_for('.login'))
    login_user(donor)
    flash("Logged in successfully.")
    # print "hi"+type(url_for(".donor_form_page"))
    return redirect(request.args.get("next") or url_for("frontend.view_donations"))
  return render_template("Login.html")

@frontend.route('createDonor', methods=['GET'])
def donor_creation_page():
    return render_template('DonorCreation.html')

def fun(s):
    try:
        if(s[-1]=='/'):
            return int(s[:-1])
        else:
            return int(s)
    except Exception:
        return None
@frontend.route('donations/', methods=['GET','POST'])
@login_required
def view_donations():
    #email = 'arunpandianp@gmail.com'
    email = current_user.email_address
    if request.method == 'GET':
        donor = db.session.query(Donor).filter_by(email_address = email).first()
        if donor.is_admin:
            donations=Donation.query.all()
        else:
            donations = donor.donations
        return render_template('view_donations.htm', donations=donations)
    elif request.method == 'POST':
        isemail = False
        if request.args.get('email'):
            isemail = True
        donation_ids = map(lambda x : fun(x),request.form.keys())
        print donation_ids
        donor = db.session.query(Donor).filter_by(email_address = email).first()
        if donor.is_admin:
            donations=Donation.query.filter(Donation.id.in_(donation_ids)).all()
        else:
            donations = donor.donations.all()
            donor_donation_ids = set(map(lambda x: x.id, donations))
            donor_accessible_donation_ids = []
            for i in donation_ids:
                if(i in donor_donation_ids):
                    donor_accessible_donation_ids.append(i)
            donation_ids = donor_accessible_donation_ids
            donations=Donation.query.filter(Donation.id.in_(donation_ids)).all()
            print donations
            return generate_zipped_receipts(donor, donations,isemail)
donation_made_text = '''Dear Donor,

  Thank you for making a difference by donating for Team Everest.  Please find your E-receips tattached with this email for your donation.

  Keep making a difference.

  Thanks & Regards,
  Team Everest
  www.teameverestindia.org
'''


def generate_zipped_receipts(donor, donations,isemail):
    pdfFiles = []
    for donation in donations:
        data = {'Amount':donation.amount, 'ReceiptNo':donation.id, 'DonationDate': donation.date, 'OrgName': "Team Everest", 'OrgAddress': "chennai", 'DonationMode': donation.mode, 'DonorName':donor.name, 'DonorAddress' : donor.address, 'Certification_Number' : "213213dsfdaf3", "WordAmount":num2words(donation.amount) }
        pdf = makePdf(data)
        pdfFiles.append(pdf)
    s = zipFiles(pdfFiles)
    if(isemail):
        file = open(s)
        sendEmail(donor.email_address, donation_made_text, file)
        return redirect(request.referrer) 
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



