import smtplib
import os

SMTPLIB_CONNECT_NO = 587


def send_message(name, email, phone, message) -> None:
    """
    Send a message via email using SMTP.

    Args:
        name (str): Sender's name.
        email (str): Sender's email address.
        phone (str): Sender's phone number.
        message (str): The message content.

    Returns:
        None

    """
    # Connect to the SMTP server (Gmail in this case)
    with smtplib.SMTP("smtp.gmail.com", SMTPLIB_CONNECT_NO) as connection:
        # Start TLS encryption for secure communication
        connection.starttls()

        # Login to the email account
        connection.login(user=os.getenv("EMAIL_USER_FROM"), password=os.getenv("PASSWORD"))

        encoded_message = message.encode('utf-8')
        decoded_message = encoded_message.decode('utf-8')

        # Send the email message
        connection.sendmail(from_addr=os.getenv('EMAIL_USER_FROM'),
                            to_addrs=os.getenv('EMAIL_USER_TO'),
                            msg=f"Subject:Track-Finance!\n\n "
                                f"Name: {name}\n\n "
                                f"Email: {email}\n\n "
                                f"Phone: {phone}\n\n "
                                f"Message: {decoded_message}")
