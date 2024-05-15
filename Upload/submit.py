from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib
import time

from config_upl import *

def sendConfirmationEmail(form:dict, admins = ADMINS):
    '''Send confirmation email upon clicking 'submit' button

        Params:
        --------
        form: dict
            completed form on webpage. As extracted by extracting_form()
        admins: list
            list of additional email adress to send the confirmation to
        
        Returns:
        ---------
        bool: whether or not the emails were sent

        '''
    # Define the multipart message
    print('sending email', flush=True)
    msg = MIMEMultipart()
    msg['From'] = 'Prisma'
    msg['Subject'] = 'Confirmation of Submission of {} ({})'.format(form['CifName'], form['SubmissionTime'])

    toaddrs = [form['Email']]
    toaddrs = set(toaddrs + admins)

    text = MIMEText('''
    Dear {} {},

    Thank you for submitting a structure ({}). We will come back to you when the calculations are finished.
                    
    Kind regards,
    The PrISMa team
    '''
    .format(form['FirstName'], form['LastName'], form['SubmissionTime']))
    
    msg.attach(text) 

    # Attach cif file to attachment
    attachment = MIMEText(form['CifContent'])
    attachment.add_header('Content-Disposition', 'attachment', filename=form['CifName'])           
    msg.attach(attachment)

    # Attach pdf file of overview
    #pdf_attachment = MIMEApplication(form['html_overview'], _subtype='pdf')
    #pdf_attachment.add_header('Content-Disposition', f'attachment; filename={form["CifBaseName"]}_overview.pdf')
    #msg.attach(pdf_attachment)

    # Attach overview submission form to message
    string = 'Submitted form:\n\n'
    for k,v in form.items():
        string += f'{k}\t{v}\n'
    overview = MIMEText(string)
    overview.add_header('Content-Disposition', 'attachment', filename='submissionForm.txt')           
    msg.attach(overview)

    msg['To'] = form['Email']

    # Define account and sending details
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)

    for to in toaddrs:
        print('Sending email to {}...'.format(to), flush=True)
        try:
            del msg['To'] # need to remove the previous 'To' header otherwise will not send
            msg['To'] = to
            server.sendmail('PrISMa', to, msg.as_string())
        except Exception as e:
            print('Error: Could not send an email to {} ({})'.format(form['Email'], e), flush=True)
        time.sleep(1)
    server.close()
    return True
