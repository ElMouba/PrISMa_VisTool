from fastapi import FastAPI
from models import results
from pdf import OverviewPDF
from submission_form import SubmissionForm
from sending import sendConfirmationEmail
import smtplib
from config_upl import *

app = FastAPI()

@app.post("/sendresults/")
def send_email(results:results):
    print('starting to send email')
    form = results.submissionform

    subform = SubmissionForm(form)
    table = subform.get_table()

    pdf = OverviewPDF(submission_form = table, models_output= results.predictions)
    pdf_bytes = pdf.get_pdfbytes()

    form['html_overview'] = pdf_bytes
    print('html added to form', flush=True)
    exception = None
    try:
        sendConfirmationEmail(form)
        send_bool = True
        exception = None

    except Exception as e:
        send_bool = False
        exception = e
        print('Email not send: {}'.format(exception), flush=True)
    
    return {"email": {"send":send_bool,
                     "Exception":exception}
    }

@app.post("/test/") 
def api_v1_test():
    print('Testing Email: OK')
    return {'test': True}


@app.post("/check_connection/") 
def check_Emailconnection():
    '''Checks the SMTP connection
    Returns
    -------
    server_status: int
        SMTP status code
        250 (Requested mail action okay, completed)
        535 (Username and Password not accepted)
        '''
    username = SENDER_EMAIL
    password = SENDER_PASSWORD
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    
    try:
        server.login(username,password)
        server_status = server.noop()[0]

    except smtplib.SMTPAuthenticationError as e:
        server_status = e.smtp_code
    server.quit()

    return {"server_status":server_status}

