import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Encoders

#Email sending module. Takes 2 arguments, receiver mail id and the fileObject of attachment. Attachment is assumed to be on disk.

def sendEmail(emailTo,attachmentFile):
  EMAIL_FROM =  "nkskalyann@gmail.com"
  EMAIL_SERVER = "smtp.gmail.com"
  SUBJECT = "Auto generated Receipt"

  msg = MIMEMultipart()
  msg['Subject'] = SUBJECT
  msg['From'] = EMAIL_FROM
  msg['To'] = emailTo
  part = MIMEBase('application', "octet-stream")
  part.set_payload(attachmentFile).read()
  Encoders.encode_base64(part)

  if hasattr(attachmentFile,"name"):
      fileName = attachmentFile.name
  else:
    fileName = "Receipt.pdf"

  part.add_header('Content-Disposition', 'attachment; filename='+fileName)

  msg.attach(part)

  server = smtplib.SMTP(EMAIL_SERVER,587)
  server.ehlo()
  server.starttls()
  server.ehlo()
  server.login(EMAIL_FROM, "123simple")
  server.sendmail(EMAIL_FROM, [emailTo], msg.as_string())
