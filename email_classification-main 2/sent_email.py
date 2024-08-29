import time
import imaplib
import email
import traceback 
import smtplib
import re

import datetime
from datetime import datetime

from connect import credentials

details = credentials()

def read_email_from_sent():
    try:
        check_response = ""

        mail = imaplib.IMAP4_SSL(details['SMTP_SERVER'], details['SMTP_PORT'])
        mail.login(details['FROM_EMAIL'],details['FROM_PWD'])
        mail.select('INBOX.Sent', readonly = False)

        data = mail.search(None, 'ALL')
        mail_ids = data[1]
        id_list = mail_ids[0].split()   
        #latest_email_id = id_list[-1]
        #data = mail.fetch(latest_email_id, '(RFC822)' )

        try:
            latest_email_id = id_list[-1]
            data = mail.fetch(latest_email_id, '(RFC822)' )
            #check_response = latest_email_id
            for response_part in data:
                    arr = response_part[0]
                    if isinstance(arr, tuple):
                        msg = email.message_from_string(str(arr[1],'utf-8'))

                        email_subject = msg['Subject']
                        email_from = msg['From']
                        email_date = msg['Date']
                        email_date = datetime.strptime(str(email_date), "%a, %d %b %Y %H:%M:%S %z")
                        email_date = email_date.strftime("%Y-%m-%d %H:%M:%S%z")
                        email_date = datetime.strptime(str(email_date), "%Y-%m-%d %H:%M:%S%z")
                        email_msg_id = msg.get('Message-ID')

                        # get message id 
                        resp, data1 = mail.fetch(latest_email_id, '(UID)' )
                        pattern_uid = re.compile(r'\d+ \(UID (?P<uid>\d+)\)')
                        match = pattern_uid.match(data1[0].decode('utf-8'))
                        msg_uid = match.group('uid')

                        if 'References' in msg:
                            go_ahead = "replied"
                            result = mail.uid('COPY', msg_uid, "INBOX.Sent.Reply_back")
                            if result[0] == 'OK':
                                mov, data1 = mail.uid('STORE', msg_uid , '+FLAGS', '(\Deleted)')
                                mail.expunge()
                            
                            reference_id = msg.get('References')
                            reference_id = reference_id.split()
                            reference_id = reference_id[0]
                            
                            return_result = {'conversation_id':reference_id,
                            'reply_date':email_date,
                            'email_status':"replied",
                            'case_status':"case closed"}


                        else:
                            go_ahead = "new sent"
                            result = mail.uid('COPY', msg_uid, "INBOX.Sent.new_sent")
                            if result[0] == 'OK':
                                mov, data1 = mail.uid('STORE', msg_uid , '+FLAGS', '(\Deleted)')
                                mail.expunge()
                            return_result = "check new sent folder"
        
        except IndexError:
            print("No new emails")
            mail.logout()
            return_result = "no new emails"
    
    except Exception as e:
        traceback.print_exc() 
        print(str(e))
        return_result = "exception"
    
    return return_result

