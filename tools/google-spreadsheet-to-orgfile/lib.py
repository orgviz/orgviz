#!/usr/bin/python3

import pickle
import sys
import os.path
from time import sleep
from oauth2client import client
from oauth2client.file import Storage
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

credentialsJson = "???"

sheetsApi = None

def setCredentialsJson(c):
    global credentialsJson 
    credentialsJson = c

def run_flow(flow, store):
    flow.redirect_uri = client.OOB_CALLBACK_URN
    authorize_url = flow.step1_get_authorize_url()

    print("Go and authorize at: ", authorize_url)

    code = get_login_code()

    try:
        credential = flow.step2_exchange(code, http=None)
    except client.FlowExchangeError as e:
        print("Auth failure: %s", str(e))
        sys.exit(1)

    store.put(credential)
    credential.set_store(store)

    return credential

def get_login_code():
    # Design choice: sleep-wait for the file, as when this script is run as a
    # service/container, etc, it allows an administrator to enter a login code
    # rather than crashing due to no TTY being available.

    while not os.path.exists("/tmp/login_code"):
        print("Waiting for login code via file: /tmp/login_code ")
        sleep(10)

    print("Login code file found")
    code = open("/tmp/login_code", "r").read()

    return code

def getCreds():
    # The cookieFilename stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    cookieFilename = os.path.abspath('/tmp/spreadsheet-reader.cookie')

    store = Storage(cookieFilename)
    creds = store.get()

    if not creds or creds.invalid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

            flow = client.flow_from_clientsecrets(credentialsJson, SCOPES)
            flow.user_agent = "spreadsheet-reader"

            creds = run_flow(flow, store)

    return creds

def getSheetsApi():
    global sheetsApi
    
    if sheetsApi == None:
        sheetsApi = build('sheets', 'v4', credentials=getCreds()).spreadsheets();

    return sheetsApi

def spreadsheetQuery(sheets, cellReference, spreadsheetId):
    return sheets.values().get(spreadsheetId=spreadsheetId, range=cellReference).execute().get('values', [])

def findColumnIndexes(sheets, spreadsheetId):
    columnIndexes = {
        "name": None,
        "title": None,
        "reports": None,
        "dmu": None,
        "sentiment": None,
        "country": None,
        "team": None,
    }

    headers = spreadsheetQuery(sheets, "A1:K1", spreadsheetId)

    for index, headerName in enumerate(headers[0]):
        headerName = headerName.strip().lower()

        columnIndexes[headerName] = index

    return columnIndexes

def tryPrintKey(person, key, columnIndexes, separator=":"):
    try: 
        if columnIndexes[key] == None: return ""

        val = person[columnIndexes[key]]

        if val.strip() == "": return ""

        return "\t" + key + separator + " " + str(person[columnIndexes[key]]) + "\n"
    except IndexError:
        return ""

def generateDot(spreadsheetId):
    sheets = getSheetsApi();

    columnIndexes = findColumnIndexes(sheets, spreadsheetId)

    people = spreadsheetQuery(sheets, "A2:K", spreadsheetId)

    ret = ""

    for person in people:
        name = person[columnIndexes["name"]]

        if name.strip() == "": continue

        ret += name + "\n"
        ret += tryPrintKey(person, "title", columnIndexes)
        ret += tryPrintKey(person, "dmu", columnIndexes)
        ret += tryPrintKey(person, "sentiment", columnIndexes)
        ret += tryPrintKey(person, "reports", columnIndexes, " ->")
        ret += tryPrintKey(person, "country", columnIndexes)
        ret += "\n"

    return ret
