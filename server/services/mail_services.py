from mailjet_rest import Client  # type: ignore
from os import getenv
from dotenv import load_dotenv
import logging

load_dotenv(dotenv_path=".env")
HOST = "in-v3.mailjet.com"
PORT = 587
USER = getenv("MAILJET_USER")
PASSWD = getenv("MAILJET_PASSWD")
sender = getenv("MAILJET_SENDER")


def send_mail(
    recipient,
    subject,
    content="<h3>Ouaf ouaf!</h3><br />",
    sender_address=sender,
    myname="Leximpact",
):
    mailjet = Client(auth=(USER, PASSWD), version="v3.1")
    data = {
        "Messages": [
            {
                "From": {"Email": sender_address, "Name": myname},
                "To": [{"Email": recipient}],
                "Subject": subject,
                "TextPart": "",
                "HTMLPart": content,
            }
        ]
    }
    result = mailjet.send.create(data=data)
    logging.info("email sent to {}".format(recipient))
    if result.status_code != 200:
        logging.error("Error in sending email: {}".format(result.json()))
