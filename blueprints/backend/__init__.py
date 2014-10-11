from __future__ import with_statement
import tempfile
from num2words import num2words
from xhtml2pdf import pisa
from jinja2 import Template
import os
import datetime
import random

from contextlib import closing
from zipfile import ZipFile, ZIP_DEFLATED

from flask import Blueprint, render_template, session, request, send_file, abort
from jinja2 import Template
from xhtml2pdf import pisa
from sqlalchemy.orm import sessionmaker
from models import db, Donor, Donation

backend = Blueprint('backend', __name__)

@backend.route('donors/', methods=['POST'])
def create_donor():
    pass

@backend.route('donations/', methods=['POST'])
def create_donation():
    print(request.form)
    donor = Donor.query.filter_by(email_address=request.form['donor']).first()
    if donor is None:
        donor = Donor(email_address=request.form['donor'])
        db.session.add(donor)
        db.session.commit()
    donation = Donation(date=request.form['donationDate'],
                        amount=request.form['donationAmount'],
                        mode=request.form['donationMode'],
                        cheque_number=request.form['chequeNumber'],
                        cheque_date=request.form['chequeDate'],
                        transcation_id=request.form['transactionId'])
    donor.donations.append(donation)
    db.session.add(donor)
    db.session.commit()
    strIO = create_receipt_pdf(donation.id)
    if strIO is not None:
        strIO.seek(0)
        return send_file(strIO, attachment_filename='{}.pdf'.format(donation.id), as_attachment=True)
    else:
        abort(400)

import StringIO
def create_receipt_pdf(donation_id):
    donation = Donation.query.get(donation_id)
    if donation is None:
        return None
    with open("receipt_template.html") as template_file:
        html = Template(template_file.read()).render({'Amount':donation.amount, 'ReceiptNo':donation.id, 'DonationDate': donation.date, 'OrgName': "Team Everest", 'OrgAddress': "Chennai", 'DonationMode': donation.mode, 'DonarAddress' : donation.donor.address})
        strIO = StringIO.StringIO()
        pisa.CreatePDF(html, dest=strIO)
        return strIO

@backend.route('donations/<int:donation_id>/receipt/', methods=['GET'])
def create_receipt(donation_id):
    strIO = create_receipt_pdf(donation_id)
    if strIO is not None:
        strIO.seek(0)
        return send_file(strIO, attachment_filename='{}.pdf'.format(donation_id), as_attachment=True)
    else:
        abort(400)

@backend.route('generate_zipped_receipts/', methods=['GET'])
def generate_zipped_receipts():
    #email = session.get('email')
    #if email is None:
    #    raise Exception("Not Logged in")
    donor = Donor("email@email.com","name","contact","address")
    donation = Donation(datetime.datetime.now(), 100, "cash", "desc")
    donor.donations.append(donation)
    db.session.add(donor)
    db.session.commit()
    donor = db.session.query(Donor).filter_by(email_address = "email@email.com")
    donations = donor.first().donations.all()
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
