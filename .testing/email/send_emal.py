import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Email configuration
sender_email = "prismastructures@gmail.com"
recipient_email = "vanherck.joren@gmail.com"
app_password = "ctjadksgrsjkabvf"


# Create the email message
msg = MIMEMultipart()
msg["From"] = sender_email
msg["To"] = recipient_email
msg["Subject"] = "Test Email from Docker Container"

body = "This is a test email sent from a Docker container."
msg.attach(MIMEText(body, "plain"))

# Establish a connection to Gmail's SMTP server
server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()

# Log in using the app password
server.login(sender_email, app_password)

# Send the email
server.sendmail(sender_email, recipient_email, msg.as_string())

# Quit the server
server.quit()
