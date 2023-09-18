from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib
import time

from config_upl import *

def sendConfirmationEmail(form:dict, admins = []):
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
    print('sending email')
    msg = MIMEMultipart()
    msg['From'] = 'Prisma'
    msg['Subject'] = 'Confirmation of Submission of {} ({})'.format(form['CifName'], form['SubmissionTime'])

    toaddrs = [form['Email']]
    toaddrs = set(toaddrs + admins)

    text = MIMEText('''
    Dear {} {},

    Thank you for submitting a structure ({}). In the attached pdf file are our platform outcomes.
                    
    If you have further questions, please contact the PRISMA team.
        
    Kind regards,
    The PRISMA team
    '''
    .format(form['FirstName'], form['LastName'], form['SubmissionTime']))
    
    msg.attach(text)

    # Define account and sending details
    username = SENDER_EMAIL
    password = SENDER_PASSWORD
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(username,password)

    # Attach cif file to attachment
    attachment = MIMEText(form['CifContent'])
    attachment.add_header('Content-Disposition', 'attachment', filename=form['CifName'])           
    msg.attach(attachment)

    # Attach pdf file of overview
    pdf_attachment = MIMEApplication(form['html_overview'], _subtype='pdf')
    pdf_attachment.add_header('Content-Disposition', f'attachment; filename={form["CifBaseName"]}_overview.pdf')
    msg.attach(pdf_attachment)

    # Attach overview submission form to message
    string = 'Submitted form:\n\n'
    for k,v in form.items():
        string += f'{k}\t{v}\n'
    overview = MIMEText(string)
    overview.add_header('Content-Disposition', 'attachment', filename='submissionForm.txt')           
    msg.attach(overview)

    msg['To'] = ', '.join(toaddrs)

    for receiver in toaddrs:
        print('Sending email to {}...'.format(receiver))
        try:
            server.sendmail('PRISMA', receiver, msg.as_string())
        except Exception as e:
            print('Error: Could not send an email to {} ({})'.format(receiver, e))
        time.sleep(1)
    server.close()
    return True