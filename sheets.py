import math

from googleapiclient.discovery import build
from datetime import date

from consts import GOOGLE_SHEETS_API_KEY, SPREADSHEET_ID


def list_sheets():
    """List all sheets in the spreadsheet with their names and IDs (gids)"""
    sheets = build("sheets", "v4", developerKey=GOOGLE_SHEETS_API_KEY).spreadsheets()
    spreadsheet = sheets.get(spreadsheetId=SPREADSHEET_ID).execute()
    
    print("Available sheets:")
    for sheet in spreadsheet.get('sheets', []):
        props = sheet.get('properties', {})
        sheet_id = props.get('sheetId')
        sheet_name = props.get('title')
        print(f"  Name: '{sheet_name}' | ID (gid): {sheet_id}")
    
    return spreadsheet.get('sheets', [])


# Returns the sheet as a list of lists, each cell is a string. 
# Ignore rows that have a first cell that is empty. 
def get_sheet_data(sheet_name=None):
    """
    Get data from a specific sheet.
    
    Args:
        sheet_name: Name of the sheet (tab). If None, uses the default/first sheet.
    
    Returns:
        The values from the specified range
    """
    sheets = build("sheets", "v4", developerKey=GOOGLE_SHEETS_API_KEY).spreadsheets()
    
    full_range = "Predictions"
    if sheet_name:
        full_range = f"{sheet_name}"
    
    result = sheets.values().get(
        spreadsheetId=SPREADSHEET_ID, 
        range=full_range
    ).execute()
    
    return result.get('values', [])

# Take sheet data and format it for Boga Bot.
def get_response(sheet_name=None):
    
    count_true = 0
    count_total = 0
    try:
        sheet_data = get_sheet_data(sheet_name)

        for row in sheet_data:
            if row[0] == '':
                continue
            if row[4] == "TRUE":
                count_true += 1
            count_total += 1
        
        percentage = math.ceil((count_true / count_total) * 100)
        current_year = date.today().year
        response = f"We have `{count_true}` predicitons completed out of {count_total} for {current_year}! That's around `{percentage}%`!"

        return response
    except:
        return "There was an error running this command. Please try again later!"
