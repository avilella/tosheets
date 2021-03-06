#!/usr/bin/python3
doc = """tosheets, send stdin to your google sheets

Usage:
  tosheets -c <cell> [-u] [-k] [-x] [-a] [-r] [-w] [-n <note>] [-s <sheet>] [--spreadsheet=<spreadsheet>] [--new-sheet=<name>] [-d <delimiter>] [-q <quote char>] [--open] [-i <csv>]
  tosheets (-h | --help)
  tosheets --version

Options:
  -h --help                     Prints help.
  --version                     Show version.
  -i CSV                        Read this CSV instead of stdin
  -u                            Update CELL(s) instead of appending.
  -k                            Keep fields as they are (do not try to convert int or float).
  -x                            Export instead of import
  -n NOTE                       insert note
  -a                            Add new sheet
  -w                            Wipe sheet clear
  -r                            Remove sheet
  -c CELL                       Start appending to CELL.
  -s SHEET                      Use sheet name SHEET, otherwise tries to use
                                TOSHEETS_SHEET (default: first visible sheet).
  -d DELIMITER                  Use DELIMITER to split each line (default: whitespace).
  -q QUOTE_CHAR                 A one-character string used to quote fields containing special characters,
                                such as the delimiter or quotechar, or which contain new-line characters.
                                (default: '"').
  --spreadsheet=<spreadsheet>   Send to the spreadsheet identified by spreadshetId
                                (ie. docs.google.com/spreadsheets/d/<spreadsheetId>/...),
                                if empty uses TOSHEETS_SPREADSHEET enviroment variable.
  --new-sheet=<name>            Create a new spreadsheet with the chosen name. Prints the
                                spreadsheetId so it can be piped/stored.
  --open                        Open a browser with the newly created sheet
"""
import webbrowser
import httplib2
import os
import re
import sys
import csv
import pandas as pd
#from StringIO import StringIO
from io import StringIO

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from docopt import docopt

import pkg_resources

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = pkg_resources.resource_filename(__name__, "client.json")
APPLICATION_NAME = 'tosheets'
SHEET_URL_FMT = 'https://docs.google.com/spreadsheets/d/%s/edit#gid=0'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-tosheets.json')

    store = Storage(credential_path)
    credentials = store.get()
    sys.argv = ['']
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

# creates a new sheet with the chosen Name
def newSheet(name):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    sheet = dict(properties={
        'autoRecalc': 'ON_CHANGE',
        'title': name,
        'locale': 'en_US',
        'timeZone': 'America/New_York'
    }, sheets=[{
        'properties': {
            'gridProperties': {'columnCount': 26, 'rowCount': 200},
            'index': 0,
            'sheetId': 0,
            'sheetType': 'GRID',
            'title': 'metrics'
        }
               },
               {
        'properties': {
            'gridProperties': {'columnCount': 26, 'rowCount': 200},
            'index': 1,
            'sheetId': 1,
            'sheetType': 'GRID',
            'title': 'isotypes'
        }
               },
               {
        'properties': {
            'gridProperties': {'columnCount': 26, 'rowCount': 200},
            'index': 2,
            'sheetId': 2,
            'sheetType': 'GRID',
            'title': 'pairs'
        }
               },
               {
        'properties': {
            'gridProperties': {'columnCount': 26, 'rowCount': 200},
            'index': 8,
            'sheetId': 8,
            'sheetType': 'GRID',
            'title': 'platform_usage'
        }
               },
               {
        'properties': {
            'gridProperties': {'columnCount': 26, 'rowCount': 200},
            'index': 3,
            'sheetId': 3,
            'sheetType': 'GRID',
            'title': 'candidates_all'
        }
               },
               {
        'properties': {
            'gridProperties': {'columnCount': 26, 'rowCount': 200},
            'index': 4,
            'sheetId': 4,
            'sheetType': 'GRID',
            'title': 'candidates_dogdog'
        }
               },
               {
        'properties': {
            'gridProperties': {'columnCount': 26, 'rowCount': 200},
            'index': 5,
            'sheetId': 5,
            'sheetType': 'GRID',
            'title': 'candidates_withmouse'
        }
               },
               {
        'properties': {
            'gridProperties': {'columnCount': 26, 'rowCount': 200},
            'index': 6,
            'sheetId': 6,
            'sheetType': 'GRID',
            'title': 'Sheet6'
        }
               },
               {
        'properties': {
            'gridProperties': {'columnCount': 26, 'rowCount': 200},
            'index': 7,
            'sheetId': 7,
            'sheetType': 'GRID',
            'title': 'Sheet7'
        }
               }
    ])

    try:
        result = service.spreadsheets().create(body=sheet).execute()
        spreadsheetId = result['spreadsheetId']
        print(spreadsheetId)
        return spreadsheetId
    except Exception as e:
        print(e)
        exit(1)


# appendToSheet that updates instead of appending, should retain virtually identical semantics
def updateSheet(values, spreadsheetId, rangeName):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    try:
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheetId, range=rangeName,
            valueInputOption='RAW', body = {'values': values}).execute()
    except Exception as e:
        print(e)
        exit(1)
    exit(0)

def appendToSheet(values, spreadsheetId, rangeName):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    try:
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheetId,
            range=rangeName,
            valueInputOption='RAW',
            body = {'values': values}).execute()
    except Exception as e:
        print(e)
        exit(1)
    exit(0)

def insertNote(this_note, spreadsheetId, sheet, cell):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    try:

        sheet_id = service.spreadsheets().get(spreadsheetId=spreadsheetId,ranges=sheet+"A1").execute().get('sheets')[0].get('properties').get('sheetId')
        request_body = {
            'requests': [{
              'updateCells': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': 0,
                    'endRowIndex': 1,
                    'startColumnIndex': 0,
                    'endColumnIndex': 1
                },
                'rows': [
                    {
                        'values': [
                            {
                                'note': this_note
                            }
                        ]
                    }
                ],
                'fields': 'note'
            }            }]
        }

        # import pdb; pdb.set_trace()
        # _debug=False; #args.debug=False
        result = service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheetId,
            body=request_body
        ).execute()

    except Exception as e:
        print(e)
        exit(1)
    exit(0)

def wipeSheet(spreadsheetId, sheet, cell):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    try:
        # import pdb; pdb.set_trace()
        # _debug=False; #args.debug=False

        clear_values_request_body = {}
        result = service.spreadsheets().values().clear(spreadsheetId=spreadsheetId, range=sheet+cell, body=clear_values_request_body).execute()

    except Exception as e:
        print(e)
        exit(1)
    exit(0)

def addSheet(spreadsheetId, sheet):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    try:
        request_body = {
            'requests': [{
                'addSheet': {
                    'properties': {
                        'title': sheet[:-1]
                    }
                }
            }]
        }

        result = service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheetId,
            body=request_body
        ).execute()
        print(sheet)

    except Exception as e:
        print(e)
        exit(1)
    exit(0)

def readFromSheet(spreadsheetId, rangeName):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheetId, range=rangeName).execute()

        header = result.get('values',[])[0]
        values = result.get('values',[])[1:]
        if not values:
            print("# No data found.")
            exit(1)
        else:
            all_data = []
            for col_id, col_name in enumerate(header):
                column_data = []
                for row in values:
                    column_data.append(row[col_id])
                ds = pd.Series(data=column_data, name=col_name)
                all_data.append(ds)
            df = pd.concat(all_data, axis=1)
            #import pdb; pdb.set_trace()
            #pass; # args.debug=False
            output = StringIO()
            df.to_csv(output,index=False)
            output.seek(0)
            print(output.read())

    except Exception as e:
        print(e)
        exit(1)
    exit(0)

def tryToConvert(x):
    try:
       return int(x)
    except ValueError:
      try:
          return float(x)
      except ValueError:
          return x.strip()


def dummyConvert(x):
    return x.strip()


# If the given ID looks like a full URL instead of an ID, extract the ID
def canonicalizeSpreadsheetId(spreadsheetId):
    match = re.match('^https?://docs.google.com/spreadsheets/d/([^/]+)', spreadsheetId)
    if match:
        return match.groups()[0]

    return spreadsheetId


def main():
    version = pkg_resources.require('tosheets')[0].version
    arguments = docopt(doc, version='tosheets ' + str(version))

    spreadsheetId = arguments['--spreadsheet']
    newSheetName = arguments['--new-sheet']

    if spreadsheetId:
        spreadsheetId = canonicalizeSpreadsheetId(spreadsheetId)

    if spreadsheetId is None and newSheetName is None:
        if not "TOSHEETS_SPREADSHEET" in os.environ:
            print("TOSHEETS_SPREADSHEET is not set and --spreadsheet was not given")
            exit(1)
        spreadsheetId = os.environ['TOSHEETS_SPREADSHEET']

    if newSheetName is not None:
        spreadsheetId = newSheet(newSheetName)

    cell = arguments['-c']
    sheet = arguments['-s']

    if sheet is None:
        if not "TOSHEETS_SHEET" in os.environ:
            sheet = ""
        else:
            sheet = os.environ['TOSHEETS_SHEET'] + "!"
    else:
        sheet += "!"

    separator = arguments['-d'] or ' '
    quote = arguments['-q'] or '"'
    keep = arguments['-k']
    reader = csv.reader(sys.stdin, delimiter=separator, quotechar=quote)

    add_sheet = arguments['-a']
    if add_sheet is not False:
        # print("Export function")
        addSheet(spreadsheetId, sheet)
        exit(0)

    this_note = arguments['-n']
    if this_note is not None:
        # print("Export function")
        insertNote(this_note, spreadsheetId, sheet, cell)
        exit(0)

    wipe_sheet = arguments['-w']
    if wipe_sheet is not False:
        # print("Export function")
        wipeSheet(spreadsheetId, sheet, cell)
        exit(0)

    export = arguments['-x']
    if export is not False:
        # print("Export function")
        readFromSheet(spreadsheetId, sheet + cell)
        exit(0)

    input_file = arguments['-i'] or None
    input_fd = sys.stdin

    if input_file is not None:
        input_fd = open(input_file)

    reader = csv.reader(input_fd, delimiter=separator, quotechar=quote)

    values = []
    for line in reader:
        values.append(list(map(dummyConvert if keep else tryToConvert, line)))

    update = arguments['-u']
    if update is False:
        appendToSheet(values, spreadsheetId, sheet + cell)
    else:
        updateSheet(values, spreadsheetId, sheet + cell)

    should_open = arguments['--open'] or False
    if should_open:
        webbrowser.open(SHEET_URL_FMT % spreadsheetId)


if __name__ == '__main__':
    main()
