from __future__ import print_function
import pickle
import os.path
import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import web_crawler
import common

# If modifying these scopes, delete the file token.pickle.
# SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1pRGiHg-zSL-UJ5lOYbhq4T2CsFrAG60ENt2z49VFNAg'
YIELD_RANGE_NAME = 'sheet1!A1:L'
HISTORY_RANGE_NAME = 'sheet1!A28:L'


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    # sheet = service.spreadsheets()
    # result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
    #                             range=SAMPLE_RANGE_NAME).execute()
    # values = result.get('values', [])
    #
    # if not values:
    #     print('No data found.')
    # else:
    #     print('Name, Major:')
    #     for row in values:
    #         # Print columns A and E, which correspond to indices 0 and 4.
    #         print('%s, %s' % (row[0], row[1]))

    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=YIELD_RANGE_NAME).execute()
    print(result)

    yield_data = web_crawler.get_yield_data()
    excel_data = make_excel_data(yield_data)
    history_data = make_history_data(yield_data)

    value_range_body = {'values': excel_data}
    value_input_option = 'USER_ENTERED'
    response = service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID,
                                                      range=YIELD_RANGE_NAME,
                                                      valueInputOption=value_input_option,
                                                      body=value_range_body).execute()
    value_range_body = {'values': history_data}
    response = service.spreadsheets().values().append(spreadsheetId=SPREADSHEET_ID,
                                                      range=HISTORY_RANGE_NAME,
                                                      valueInputOption=value_input_option,
                                                      body=value_range_body).execute()

    formatting_request = make_excel_format()
    request = service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=formatting_request).execute()


def make_excel_data(yield_data):
    values = [[''] * len(common.COLUMNS) for i in range(len(common.ROWS))]
    values[0] = common.COLUMNS

    for country in common.COUNTRIES:
        if yield_data.get(country) is None:
            continue
        values[get_y(country)][get_x(common.ROWS[0])] = country

        for yield_step in common.YIELD_STEPS:
            if yield_data[country].get(yield_step) is None:
                continue
            values[get_y(country)][get_x(yield_step)] = yield_data[country][yield_step]
        min_yield = values[get_y(country)][get_x(common.YIELD_STEPS[0])]
        max_yield = values[get_y(country)][get_x(common.YIELD_STEPS[-1])]
        if min_yield != '' and max_yield != '':
            values[get_y(country)][get_x(common.YIELD_GAP_INFO[0])] = (
                str(round(float(max_yield) - float(min_yield), 4)))

    print(values)
    return values


def make_history_data(yield_data):
    now = datetime.datetime.now()
    now_datetime = now.strftime('%Y-%m-%d %H:%M')
    history_data = [now_datetime]

    for target in common.HISTORY_TARGET:
        if yield_data.get(target) is None:
            continue
        min_yield = yield_data[target].get(common.YIELD_STEPS[0])
        max_yield = yield_data[target].get(common.YIELD_STEPS[-1])
        if min_yield is not None and max_yield is not None:
            history_data.append(str(round(float(max_yield) - float(min_yield), 4)))
        else:
            history_data.append('')

    print(history_data)
    return [history_data]


def get_y(name):
    return common.ROWS.index(name)


def get_x(name):
    return common.COLUMNS.index(name)


def make_excel_format():
    empty_format_range = {
        'sheetId': 0,
        'startRowIndex': 1,
        'endRowIndex': 26,
        'startColumnIndex': 3,
        'endColumnIndex': 11,
    }
    minus_format_range = {
        'sheetId': 0,
        'startRowIndex': 1,
        'endRowIndex': 26,
        'startColumnIndex': 3,
        'endColumnIndex': 11,
    }
    requests = [
        {
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [empty_format_range],
                    'booleanRule': {
                        'condition': {
                            'type': 'TEXT_EQ',
                            'values': [{
                                'userEnteredValue': ''
                            }]
                        },
                        'format': {
                            'backgroundColor': {
                                'green': 0.7,
                                'red': 0.7,
                                'blue': 0.7
                            }
                        }
                    }
                },
                'index': 0
            },
        },
        {
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [minus_format_range],
                    'booleanRule': {
                        'condition': {
                            'type': 'NUMBER_LESS',
                            'values': [{
                                'userEnteredValue': '0'
                            }]
                        },
                        'format': {
                            'text_format': {
                                'foregroundColor': {
                                    'red': 0.7
                                }
                            }
                        }
                    }
                },
                'index': 1
            }
        },
        {
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [{
                        'sheetId': 0,
                        'startRowIndex': 27,
                        'endRowIndex': 50,
                        'startColumnIndex': 1,
                        'endColumnIndex': 6,
                    }],
                    'booleanRule': {
                        'condition': {
                            'type': 'NUMBER_LESS',
                            'values': [{
                                'userEnteredValue': '0'
                            }]
                        },
                        'format': {
                            'text_format': {
                                'foregroundColor': {
                                    'red': 0.7
                                }
                            }
                        }
                    }
                },
                'index': 1
            }
        }
    ]
    body = {
        'requests': requests
    }
    return body


if __name__ == '__main__':
    print("Start Global Yield Curve Generator")
    main()
    print("End Global Yield Curve Generator")
