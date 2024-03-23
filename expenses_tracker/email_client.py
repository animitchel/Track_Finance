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
        connection.login(user='jeremylawrence112@gmail.com', password=os.getenv("PASSWORD"))

        # Send the email message
        connection.sendmail(from_addr='jeremylawrence112@gmail.com',
                            to_addrs='animitchel24@gmail.com',
                            msg=f"Subject:Mitchel's Blog!\n\n "
                                f"Name: {name}\n\n "
                                f"Email: {email}\n\n "
                                f"Phone: {phone}\n\n "
                                f"Message: {message.encode('utf-8')}")
