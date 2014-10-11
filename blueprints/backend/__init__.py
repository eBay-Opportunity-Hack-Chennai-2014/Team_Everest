import os
import datetime

from flask import Blueprint, render_template, session, request
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
        data = {'Amount':donation.amount, 'ReceiptNo':donation.id, 'DonationDate': donation.date, 'OrgName': "Team Everest", 'OrgAddress': "chennai", 'DonationMode': donation.mode, 'DonarAddress' : donor.address}
         pdf = makePdf(data)
         pdfFiles.append(pdf)
    #XXXXXX
    return render_template('test.html')


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
