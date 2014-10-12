import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.mime.text import MIMEText
from email import Encoders

#Email sending module. Takes 2 arguments, receiver mail id and the fileObject of attachment. Attachment is assumed to be on disk.

def sendEmail(emailTo,attachmentFile):
  EMAIL_FROM =  "teameverest.ohack@gmail.com"
  EMAIL_SERVER = "smtp.gmail.com"
  SUBJECT = "Auto generated Receipt"

  bodyText = '''Dear <NAME>,

  Thank you for making a difference by donating Rs <Amount> on <Date> for Team Everest.  Please find your E-receipt attached with this email for your donation.

  Keep making a difference.

  Thanks & Regards,
  Team Everest
  www.teameverestindia.org
  '''
  emailBody = MIMEText(bodyText,"plain")
  msg = MIMEMultipart()
  msg['Subject'] = SUBJECT
  msg['From'] = EMAIL_FROM
  msg['To'] = emailTo
  part = MIMEBase('application', "octet-stream")
  part.set_payload(attachmentFile.read())
  Encoders.encode_base64(part)

  if hasattr(attachmentFile,"name"):
    fileName = attachmentFile.name
  else:
    fileName = "Receipt.pdf"

  part.add_header('Content-Disposition', 'attachment; filename='+fileName)

  msg.attach(part)
  msg.attach(emailBody)

  server = smtplib.SMTP(EMAIL_SERVER,587)
  server.ehlo()
  server.starttls()
  server.ehlo()
  server.login(EMAIL_FROM, "ebayohack")
  server.sendmail(EMAIL_FROM, [emailTo], msg.as_string())
