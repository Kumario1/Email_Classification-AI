import time
import imaplib
import email
import traceback 
import smtplib
import re

import datetime
from datetime import datetime


from connect import credentials
from classification_model import classifier

details = credentials()

def read_email_from_mailbox():
    try:
        check_response = ""

        mail = imaplib.IMAP4_SSL(details['SMTP_SERVER'], details['SMTP_PORT'])
        mail.login(details['FROM_EMAIL'],details['FROM_PWD'])
        mail.select('inbox', readonly = False)

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
                        
                        if 'References' in msg:
                            go_ahead = "no"
                            reference_id = msg.get('References')
                            reference_id = reference_id.split()
                            reference_id = reference_id[0]
                        else:
                            go_ahead = "yes"

                        email_subject = msg['Subject']
                        email_from = msg['From']
                        email_date = msg['Date']
                        email_date = datetime.strptime(str(email_date), "%a, %d %b %Y %H:%M:%S %z")
                        email_date = email_date.strftime("%Y-%m-%d %H:%M:%S%z")
                        email_date = datetime.strptime(str(email_date), "%Y-%m-%d %H:%M:%S%z")
                        email_msg_id = msg.get('Message-ID')


                        if msg.is_multipart():
                            email_content = ''
                            for part in msg.get_payload():
                                if part.get_content_type() == 'text/plain':
                                    email_content += part.get_payload()
                        else:
                            email_content = msg.get_payload()

                        print('From : ' + email_from + '\n')
                        print('Subject : ' + email_subject + '\n')
                        print('Content : ' + email_content + '\n')
            
            if go_ahead == "yes":
                # call classification
                folder = classifier(email_content)
                print('Folder : ' + folder + '\n')

                resp, data1 = mail.fetch(latest_email_id, '(UID)' )
                pattern_uid = re.compile(r'\d+ \(UID (?P<uid>\d+)\)')
                match = pattern_uid.match(data1[0].decode('utf-8'))
                msg_uid = match.group('uid')

                #mail.select('personal')
                if folder == 'Technical issue':
                    result = mail.uid('COPY', msg_uid, 'INBOX.Technical_issue')
                    if result[0] == 'OK':
                        mov, data1 = mail.uid('STORE', msg_uid , '+FLAGS', '(\Deleted)')
                        mail.expunge()
                    mail.select('INBOX.Technical_issue')

                elif folder == 'Billing inquiry':
                    result = mail.uid('COPY', msg_uid, 'INBOX.Billing_inquiry')
                    if result[0] == 'OK':
                        mov, data1 = mail.uid('STORE', msg_uid , '+FLAGS', '(\Deleted)')
                        mail.expunge()
                    mail.select('INBOX.Billing_inquiry')

                elif folder == 'Cancellation request':
                    result = mail.uid('COPY', msg_uid, 'INBOX.Cancellation_request')
                    if result[0] == 'OK':
                        mov, data1 = mail.uid('STORE', msg_uid , '+FLAGS', '(\Deleted)')
                        mail.expunge()
                    mail.select('INBOX.Cancellation_request')

                elif folder == 'Product inquiry':
                    print("inside product inquiry")
                    result = mail.uid('COPY', msg_uid, "INBOX.Product_inquiry")
                    print(result)
                    if result[0] == 'OK':
                        mov, data1 = mail.uid('STORE', msg_uid , '+FLAGS', '(\Deleted)')
                        mail.expunge()
                    mail.select('INBOX.Product_inquiry')
                
                elif folder == 'Refund request':
                    result = mail.uid('COPY', msg_uid, 'INBOX.Refund_request')
                    if result[0] == 'OK':
                        mov, data1 = mail.uid('STORE', msg_uid , '+FLAGS', '(\Deleted)')
                        mail.expunge()
                    mail.select('INBOX.Refund_request')

                mail.uid('STORE', msg_uid , '-FLAGS', '(\Seen)') # Marks email as Unseen/Unread
                
                return_result = {'email_id':email_from,
                'conversation_id':email_msg_id,
                'department':folder,
                'email_date':email_date,
                'email_status': "email received",
                'case_status': "case opened"}
                #disconnect(mail)
                #mail.logout()
                #time.sleep(10)
        
            elif go_ahead == "no":
                return_result = {'conversation_id':reference_id,
                'email_status':"reply back",
                'case_status': "case opened"}

                resp, data1 = mail.fetch(latest_email_id, '(UID)' )
                pattern_uid = re.compile(r'\d+ \(UID (?P<uid>\d+)\)')
                match = pattern_uid.match(data1[0].decode('utf-8'))
                msg_uid = match.group('uid')
                
                result = mail.uid('COPY', msg_uid, 'INBOX.Reply_back')
                if result[0] == 'OK':
                    mov, data1 = mail.uid('STORE', msg_uid , '+FLAGS', '(\Deleted)')
                    mail.expunge()

        except IndexError:
            print("No new emails")
            return_result = "no new emails"
        mail.logout()
        #time.sleep(30)
        
        

    except Exception as e:
        traceback.print_exc() 
        print(str(e))
        return_result = "exception"
    
    return return_result

