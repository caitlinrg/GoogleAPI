import os.path
import base64
from datetime import date

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def main():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())



  try:
    
    sender_email = 'concierge@pacerevenue.com'

    # Get messages that match the query
    query = f'from:{sender_email}'

    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)

    msg_res = service.users().messages()
    resultsmsg = msg_res.list(q=query, userId='me', maxResults=30).execute()
    messages = resultsmsg.get('messages', [])

    today = date.today()
    print("Today's date:", today)

    if not messages:
        print('No messages found.')
    else:
        for msg in messages:
            msg_dict = msg_res.get(userId='me', id=msg['id']).execute()
            #print(msg_dict)
            msg_headers = msg_dict['payload']['headers']
            #print(msg_headers)
            msg_from = filter(lambda hdr: hdr['name'] == 'From', msg_headers)
            msg_subj = filter(lambda hdr: hdr['name'] == 'Subject', msg_headers)
            msg_from = list(msg_from)[0]
            msg_subj = list(msg_subj)[0]

            # Check if message has any attachments
            payload = msg_dict['payload']

            if 'parts' in payload:
                for part in payload['parts']:
                    # Check if part is an attachment
                    if part['filename']:
                        filename = part['filename']
                        att_id=part['body']['attachmentId']
                        att=service.users().messages().attachments().get(userId="me", messageId=msg['id'],id=att_id).execute()
                        data=att['data']

                        file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                        path = str(today) + "/" + part['filename']
                        os.makedirs(os.path.dirname(path), exist_ok=True)

                        with open(path, 'wb') as f:
                            f.write(file_data)

                        x = service.users().messages().trash(userId="me",id=msg["id"]).execute()

  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()