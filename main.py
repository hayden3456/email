import imaplib
import smtplib
import email
import time
from email.header import decode_header
from dotenv import load_dotenv
import os

# Email account credentials
username = 'hayden@protogenesis.us'
password = 

# IMAP server configuration (example is for Gmail)
imap_server = 'imap.gmail.com'
imap_port = 993

# SMTP server configuration for sending emails
smtp_server = 'smtp.gmail.com'
smtp_port = 587

# Recipients to forward the email to
forward_to = ['hayden@protogenesis.us', 'hjconstas@gmail.com']

def check_and_forward_emails():
    print("Connecting to IMAP server...")
    mail = imaplib.IMAP4_SSL(imap_server, imap_port)
    mail.login(username, password)
    mail.select('inbox')

    print("Searching for unseen emails...")
    _, search_data = mail.search(None, 'UNSEEN')
    for num in search_data[0].split():
        print(f"Processing email ID: {num}")
        _, data = mail.fetch(num, '(RFC822)')
        _, bytes_data = data[0]

        email_message = email.message_from_bytes(bytes_data)
        email_to = email_message['To']

        print(f"Email subject: {decode_header(email_message['Subject'])[0][0]}")

        # Check if 'outreach@protogenesis.us' is in the 'To' field
        if 'outreach@protogenesis.us' in email_to:
            send_email(email_message)
        else:
            print("Email does not contain 'outreach@protogenesis.us' in the 'To' field. Skipping forwarding.")

    mail.close()
    mail.logout()
    print("Logged out of IMAP server.")


def send_email(message):
    print("Forwarding email...")
    forwarded_message = email.message.EmailMessage()

    if message.is_multipart():
        # Initialize an empty string to hold the text parts
        body = ''
        for part in message.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if "attachment" not in content_disposition:
                # Concatenate text parts only
                if "text" in content_type:
                    part_payload = part.get_payload(decode=True)
                    if part_payload:
                        body += part_payload.decode()
        # Set the concatenated text as the content of the forwarded message
        forwarded_message.set_content(body)
    else:
        # For non-multipart emails, set the content directly
        payload = message.get_payload(decode=True)
        if payload:
            forwarded_message.set_content(payload.decode())

    # Set the forwarded message's headers
    forwarded_message['From'] = username
    forwarded_message['To'] = ', '.join(forward_to)
    forwarded_message['Subject'] = 'Fwd: ' + decode_header(message['Subject'])[0][0]

    # Send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(username, password)
        server.send_message(forwarded_message)
    print("Email forwarded successfully.")

while True:
    check_and_forward_emails()
    print("Sleeping for 30 minutes...")
    time.sleep(1800)
