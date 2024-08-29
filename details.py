import json
import random

from read_email import read_email_from_mailbox
from sent_email import read_email_from_sent

API_EMAIL_PROCESS_ADD = ""

with open("agent.json", 'r') as j:
    department_dict = json.loads(j.read())


def get_email_details():
    email_details = read_email_from_mailbox()
    print("details_file:",email_details)
    if email_details != "no new emails" and email_details != "exception" and email_details['email_status'] != "reply back":
            agents = department_dict[email_details['department']]
            agent = random.choice(list(agents.values()))
            email_details['agent'] = agent
    return email_details

def get_sent_details():
    email_details = read_email_from_sent()
    return email_details
        