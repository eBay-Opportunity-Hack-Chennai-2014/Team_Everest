import os
import datetime

from flask import Blueprint, render_template, session, request, send_file, abort
from jinja2 import Template
from xhtml2pdf import pisa
from sqlalchemy.orm import sessionmaker
from models import db, Donor, Donation

backend = Blueprint('backend', __name__)

# @backend.route('/generate_zipped_receipts/', methods=['GET'])
# def generate_zipped_receipts():
#     #email = session.get('email')
#     #if email is None:
#     #    raise Exception("Not Logged in")
#     import pdb
#     #pdb.set_trace()
#     #print request.form
#     donor = Donor("email@email.com","name","contact","address")
#     donation = Donation(datetime.datetime.now(), 100, "cash", "desc")
#     donor.donations.append(donation)
#     #db.session.add(donation)
#     db.session.add(donor)
#     db.session.commit()
#     #print donor
#     #donation.donor_id = donor.id
#     donor = db.session.query(Donor).filter_by(email_address = "email@email.com")
#     donations = donor.first().donations.all()
#     pdfFiles = []
#     for donation in donations:
#         data = {'Amount':donation.amount, 'ReceiptNo':donation.id, 'DonationDate': donation.date, 'OrgName': "Team Everest", 'OrgAddress': "chennai", 'DonationMode': donation.mode, 'DonarAddress' : donor.address}
#         pdf = makePdf(data)
#         pdfFiles.append(pdf)
#     #XXXXXX
#     return render_template('test.html')
#

@backend.route('donations/', methods=['POST'])
def create_donation():
    donor = Donor("email@email.com","name","contact","address")
    donation = Donation(datetime.datetime.now(), 100, "cash", "desc")
    donor.donations.append(donation)
    db.session.add(donor)
    db.session.commit()

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

# def convertHtmlToPdf(sourceHtml):
#     resultFile = tempfile.NamedTemporaryFile(prefix='receipt_', suffix='.pdf', dir='/tmp', delete=False)
#     # convert HTML to PDF 
#     pisaStatus = pisa.CreatePDF(
#             sourceHtml,                # the HTML to convert
#             dest=resultFile)           # file handle to recieve result
#     return resultFile.name

@backend.route('donations/<int:donation_id>/receipt/', methods=['GET'])
def create_receipt(donation_id):
    strIO = create_receipt_pdf(donation_id)
    if strIO is not None:
        strIO.seek(0)
        return send_file(strIO, attachment_filename='{}.pdf'.format(donation_id), as_attachment=True)
    else:
        abort(400)
