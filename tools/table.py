import gspread
from google.oauth2.service_account import Credentials

sheet_id = "1tJJxCy0nzT3L3dYB8VtzCzkIi_CAZlsMOX_mrGNQqks"
scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]
creds = Credentials.from_service_account_file('credentials.json', scopes=scopes)
client = gspread.authorize(creds)

workbook = client.open_by_key(sheet_id)

def addTableLink(link_name: str, link: str, company_name: str, web: bool, company_id: int):
    sheet = workbook.worksheet("Лист1")
    values_list = sheet.col_values(5)
    
    sheet.update_cell(len(values_list) + 1, 1, link)
    sheet.update_cell(len(values_list) + 1, 2, 0)
    sheet.update_cell(len(values_list) + 1, 3, 0)
    sheet.update_cell(len(values_list) + 1, 4, company_name)
    sheet.update_cell(len(values_list) + 1, 5, link_name)
    sheet.update_cell(len(values_list) + 1, 6, web)
    sheet.update_cell(len(values_list) + 1, 7, company_id)

def checkTable(link_names):
    sheet = workbook.worksheet("Лист1")
    values_list = sheet.col_values(5)

    for link_name in link_names:
        if values_list.count(link_name) != 0:
            return False
    return True