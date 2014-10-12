from __future__ import with_statement
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

backend = Blueprint('backend', __name__)

@backend.route('create_donor/', methods=['POST'])
def create_donor():
    print(request.form)
    donor = Donor.query.filter_by(email_address=request.form['email']).first()
    if donor is not None:
        abort(400)
    donor = Donor(email_address=request.form['email'], name=request.form['name'], contact_number=request.form['contact_number'], address=request.form['address'])
    db.session.add(donor)
    db.session.commit()
    return redirect(request.referrer)

def create_donation(form):
    donor = Donor.query.filter_by(email_address=form['donor']).first()
    if donor is None:
        donor = Donor(email_address=form['donor'])
        db.session.add(donor)
        db.session.commit()
    donation = Donation(date=form['donationDate'],
                        amount=form['donationAmount'],
                        mode=form['donationMode'],
                        cheque_number=form['chequeNumber'],
                        cheque_date=form['chequeDate'],
                        transcation_id=form['transactionId'])
    donor.donations.append(donation)
    db.session.add(donor)
    db.session.commit()
    return donation

@backend.route('create_donation/', methods=['POST'])
def create_donation_and_return():
    donation = create_donation(request.form)
    return redirect(request.referrer)

@backend.route('create_donation_and_return_pdf/', methods=['POST'])
def create_donation_and_return_pdf():
    donation = create_donation(request.form)
    strIO = create_receipt_pdf(donation.id)
    if strIO is not None:
        strIO.seek(0)
        return send_file(strIO, attachment_filename='{}.pdf'.format(donation.id), as_attachment=True)
    else:
        abort(400)

@backend.route('create_donation_and_email_pdf/', methods=['POST'])
def create_donation_and_email_pdf():
    donation = create_donation(request.form)
    strIO = create_receipt_pdf(donation.id)
    if strIO is not None:
        strIO.seek(0)
        sendEmail(donation.donor.email_address, strIO)
        return redirect(request.referrer)
    else:
        abort(400)

def create_receipt_pdf(donation_id):
    donation = Donation.query.get(donation_id)
    if donation is None:
        return None
    with open("receipt_template.html") as template_file:
        html = Template(template_file.read()).render({'Amount':donation.amount, 'ReceiptNo':donation.id, 'DonationDate': donation.date, 'OrgName': "Team Everest", 'OrgAddress': "Chennai", 'DonationMode': donation.mode, 'DonarAddress' : donation.donor.address})
        strIO = StringIO.StringIO()
        pisa.CreatePDF(html, dest=strIO)
        return strIO

@backend.route('generate_zipped_receipts/', methods=['GET'])
def generate_zipped_receipts():
    #email = session.get('email')
    #if email is None:
    #    raise Exception("Not Logged in")
    donor = Donor("email@email.com","name","contact","address")
    donation = Donation(datetime.datetime.now(), 100, "cash")
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

"""take a list of file names and return a fd for the zipped file"""
def zipFilesFromSIO(sios):
    s = str(random.randint(0,10000000))
    s = "archivename"+s+".zip"    
    z = ZipFile(s, "w", ZIP_DEFLATED)
    i=0
    for sio in sios:
        i+=1
        z.writestr(str(i)+".pdf",sio.getvalue() )
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


@backend.route('donations/<int:donation_id>/receipt/', methods=['GET'])
def create_receipt(donation_id):
    strIO = create_receipt_pdf(donation_id)
    if strIO is not None:
        strIO.seek(0)
        return send_file(strIO, attachment_filename='{}.pdf'.format(donation_id), as_attachment=True)
    else:
        abort(400)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in current_app.config.get('ALLOWED_EXTENSIONS')

@backend.route('excel', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            r = random.randint(0,10000000)
            file_name = os.path.join(current_app.config.get('UPLOAD_FOLDER'), str(r) + filename)
            file.save(os.path.join(file_name))
            donation_ids = readExcel(file_name)
            if(request.query_string.find("check=1")!=-1):
                pdfs = []
                for donation_id in donation_ids:
                    pdf = create_receipt_pdf(donation_id)
                    pdfs.append(pdf)
                s = zipFilesFromSIO(pdfs)
                response_body = open(s).read()
                os.remove(s)
                headers = {"Content-Disposition": "attachment; filename=receipt.zip"}
                return make_response((response_body,'200', headers))
            os.remove(file_name)
            return render_template("BulkUploadSuccess.html") 
    else:
            print "sda"
            return render_template("BulkUpload.html")

#returns list of donation ids created
def readExcel(inputFile):
    donation_ids = []
    fields = {"DonationDate":"date","Amount":"amount","DonationMode":"mode","ModeDescription":"mode_description","DonorEmail":"email_address","Name":"name","ContactNo":"contact_number","Address":"address"}
    order_of_fields = {}
    workbook = xlrd.open_workbook(inputFile)
    worksheet = workbook.sheet_by_index(0)
    num_rows = worksheet.nrows - 1 
    num_cells = worksheet.ncols - 1 
    curr_row = -1
    if num_cells > 0:
        curr_row += 1
        curr_cell = -1
        while curr_cell < num_cells:
            curr_cell += 1
            cell_value = worksheet.cell_value(curr_row, curr_cell)
            order_of_fields[cell_value] = curr_cell
    while curr_row < num_rows:
        row = []
        curr_row += 1
        row = worksheet.row(curr_row)
        print 'Row:', curr_row
        curr_cell = -1
        while curr_cell < num_cells:
            curr_cell += 1
            cell_type = worksheet.cell_type(curr_row, curr_cell)
            cell_value = worksheet.cell_value(curr_row, curr_cell)
            if(cell_type > 4 or cell_type == 0):
            	row.append(None)
            elif(cell_type == 3):
                year, month, day, hour, minute, second = xlrd.xldate_as_tuple(cell_value, workbook.datemode)
	        row.append(datetime.datetime(year, month, day, hour, minute, second))
            else:
               row.append(cell_value)
               
        email = row[order_of_fields["DonorEmail"]].value
        if not email:
            raise Exception("no email");
        donor = get_donor_by_email(email)
        if not donor:
            name = row[order_of_fields["Name"]].value
            address = row[order_of_fields["Address"]].value
            contact_number = row[order_of_fields["ContactNo"]].value
            donor = Donor(email, name, contact_number, address)
        date = row[order_of_fields["DonationDate"]].value
        year, month, day, hour, minute, second = xlrd.xldate_as_tuple(date, workbook.datemode)
	date = datetime.datetime(year, month, day, hour, minute, second)
        amount = row[order_of_fields["Amount"]].value
        mode = row[order_of_fields["DonationMode"]].value
        mode_description = row[order_of_fields["ModeDescription"]].value
        donation = Donation(date, amount, mode, mode_description)
        donor.donations.append(donation)
        db.session.add(donor)
        db.session.commit()  
        donation_ids.append(donation.id)     
    return donation_ids
def get_donor_by_email(email):
    donor = db.session.query(Donor).filter_by(email_address = email)
    return donor.first()
