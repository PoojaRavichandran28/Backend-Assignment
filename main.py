import os.path
from dateutil import parser

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from db_connection import create_database_if_not_exists, create_email_data_table, insert_email_data
from rule_execution import execute_rules


CLIENT_SECRET_FILE = 'credentials.json'
API_NAME = 'gmail'
API_VERSION = 'v1'
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

STRF_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_gmail_service():
  '''
  Checks if token.json file exists. If file exists, get the credentials and establish connection with gmail api.
  If token.json file does not exists, asks for signing into gmail account and then creates oke.json file.
  If token.json file expires, error will be raised.
  :return:  service object to interact with gmail api endpoints
  '''
  creds = None

  if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json')

  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE, SCOPES)
      creds = flow.run_local_server(port=0)

    with open('token.json', 'w') as token:
      token.write(creds.to_json())

  service = build(API_NAME, API_VERSION, credentials=creds)
  return service


def fetch_mails(service):
  '''
  This function connects with gmail api's /messages/ endpoint and fetches the mails from the INBOX folder.
  The required data alone is formatted and returned as a list of dictionaries
  :param service: object
  :return formatted_data: [{'message_id': String, 'message': String, 'labels': List,
  'From': String, 'To': String, 'Subject: String', 'Date': String},......]
  '''
  try:
    results = service.users().messages().list(userId="me", labelIds='INBOX').execute()
    messages = results.get('messages', [])
    if not messages:
        print('No messages found')
    else:
      formatted_data = []
      for message in messages:
        new_dict = dict()
        msg = service.users().messages().get(userId="me", id=message['id']).execute()
        new_dict['message_id'] = msg['id']
        new_dict['message'] = msg['snippet']
        new_dict['labels'] = msg['labelIds']
        for data in msg['payload']['headers']:
          if data['name'] in ('From', 'To', 'Subject'):
            new_dict[data['name']] = data['value']
          elif data['name'] == 'Date':
            timestamp_datetime = parser.parse(data['value'])
            new_dict['Date'] = timestamp_datetime.strftime(STRF_FORMAT)
        formatted_data.append(new_dict)
      return formatted_data

  except HttpError as error:
    print(f"An error occurred: {error}")


def store_to_db(formatted_data):
  '''
  Establishes connection with the database.
  Creates the database if it doesn't exist earlier.
  Creates the table name if it doesn't exist earlier.
  Inserts the formatted data into the email_data table
  :param formatted_data: list of dictionaries
  :return: 1 if success else error message
  '''
  try:
    create_database_if_not_exists()
    create_email_data_table()
    for data in formatted_data:
      insert_email_data(data)
    return 1

  except Exception as e:
    return f'Error while storing data to db: {e}'


def main():
  '''
  Step 1: Establishes connection with gmail api
  Step 2: Using gmail api, fetches mails for Inbox and format the required data
  Step 3: Stores the formatted data to email_data table
  Step 4: Executes the rules and mark the mail as Read/Unread and move them to the specified folder
  '''
  service = get_gmail_service()
  formatted_data = fetch_mails(service)
  store_to_db(formatted_data)
  execute_rules(formatted_data, service)


if __name__ == "__main__":
  main()