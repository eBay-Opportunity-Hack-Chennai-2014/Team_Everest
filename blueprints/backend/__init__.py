from __future__ import with_statement
import tempfile
from xhtml2pdf import pisa
from jinja2 import Template
import os
import datetime
import random

from contextlib import closing
from zipfile import ZipFile, ZIP_DEFLATED

from flask import Blueprint, render_template, session, request, make_response
from sqlalchemy.orm import sessionmaker
from models import db, Donor, Donation

backend = Blueprint('backend', __name__)

@backend.route('/generate_zipped_receipts/', methods=['GET'])
def generate_zipped_receipts():
    #email = session.get('email')
    #if email is None:
    #    raise Exception("Not Logged in")
    import pdb
    #pdb.set_trace()
    #print request.form
    donor = Donor("email@email.com","name","contact","address")
    donation = Donation(datetime.datetime.now(), 100, "cash", "desc")
    donor.donations.append(donation)
    #db.session.add(donation)
    db.session.add(donor)
    db.session.commit()
    #print donor
    #donation.donor_id = donor.id
    donor = db.session.query(Donor).filter_by(email_address = "email@email.com")
    donations = donor.first().donations.all()
    pdfFiles = []
    for donation in donations:
        data = {'Amount':donation.amount, 'ReceiptNo':donation.id, 'DonationDate': donation.date, 'OrgName': "Team Everest", 'OrgAddress': "chennai", 'DonationMode': donation.mode, 'DonarAddress' : donor.first().address}
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
    templateString = open("template.html").read()
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
