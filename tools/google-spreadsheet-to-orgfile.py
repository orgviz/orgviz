#!/usr/bin/python3

import configargparse

parser = configargparse.ArgumentParser(default_config_files=["~/.spreadsheet-reader.cfg"]);
parser.add_argument("--credentialsJson", required=True)
parser.add_argument("--spreadsheetId", required=True)
parser.add_argument("--cookieFilename", default = "~/.spreadsheet-reader.cookie")
args = parser.parse_args();

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def getCreds():
    cookieFilename = os.path.abspath(os.path.expanduser(args.cookieFilename))

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    creds = None
    # The file args.cookieFilename stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(cookieFilename):
        with open(cookieFilename, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(args.credentialsJson, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(cookieFilename, 'wb') as token:
            pickle.dump(creds, token)

    return creds

def getSheetsApi():
    return build('sheets', 'v4', credentials=getCreds()).spreadsheets();

def spreadsheetQuery(sheets, cellReference):
    return sheets.values().get(spreadsheetId=args.spreadsheetId, range=cellReference).execute().get('values', [])

def findColumnIndexes(sheets):
    columnIndexes = {
        "name": None,
        "title": None,
        "reports": None,
        "dmu": None,
        "sentiment": None,
        "country": None,
        "team": None,
    }

    headers = spreadsheetQuery(sheets, "A1:K1")

    for index, headerName in enumerate(headers[0]):
        headerName = headerName.strip().lower()

        columnIndexes[headerName] = index

    return columnIndexes

def tryPrintKey(person, key, columnIndexes, separator=":"):
    try: 
        if columnIndexes[key] == None: return

        val = person[columnIndexes[key]]

        if val.strip() == "": return

        print("\t" + key + separator + "", person[columnIndexes[key]])
    except IndexError:
        pass


def main():
    sheets = getSheetsApi();

    columnIndexes = findColumnIndexes(sheets)

    people = spreadsheetQuery(sheets, "A2:K")

    for person in people:
        name = person[columnIndexes["name"]]

        if name.strip() == "": continue

        print (name)
        tryPrintKey(person, "title", columnIndexes)
        tryPrintKey(person, "dmu", columnIndexes)
        tryPrintKey(person, "sentiment", columnIndexes)
        tryPrintKey(person, "reports", columnIndexes, " ->")
        tryPrintKey(person, "country", columnIndexes)

        print(" ")

if __name__ == '__main__':
    main()
