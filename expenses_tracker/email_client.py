import smtplib
import os
from email.message import EmailMessage

SMTPLIB_CONNECT_NO = 587


def send_message(name, email, phone, message, pdf=None) -> None:
    """
    Send a message via email using SMTP.

    Args:
        pdf:
        name (str): Sender's name.
        email (str): Sender's email address.
        phone (str): Sender's phone number.
        message (str): The message content.

    Returns:
        None

    """
    encoded_message = message.encode('utf-8')
    decoded_message = encoded_message.decode('utf-8')

    # Email details
    sender_email = os.getenv('EMAIL_USER_FROM')
    recipient_email = os.getenv('EMAIL_USER_TO')
    subject = "Track-Finance"
    body = f"Name: {name}\n\nEmail: {email}\n\nPhone: {phone}\n\nMessage: {decoded_message}"

    # Create the email message
    msg = EmailMessage()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.set_content(body)

    if pdf:
        msg.add_attachment(pdf, maintype='application', subtype='pdf', filename='document.pdf')

    # Connect to the SMTP server (Gmail in this case)
    with smtplib.SMTP("smtp.gmail.com", SMTPLIB_CONNECT_NO) as connection:
        # Start TLS encryption for secure communication
        connection.starttls()

        # Login to the email account
        connection.login(user=os.getenv("EMAIL_USER_FROM"), password=os.getenv("PASSWORD"))

        # Send the email message
        # connection.sendmail(from_addr=os.getenv('EMAIL_USER_FROM'),
        #                     to_addrs=os.getenv('EMAIL_USER_TO'),
        #                     msg=f"Subject:Track-Finance!\n\n "
        #                         f"Name: {name}\n\n "
        #                         f"Email: {email}\n\n "
        #                         f"Phone: {phone}\n\n "
        #                         f"Message: {decoded_message}")

        connection.send_message(msg)
