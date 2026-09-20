import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    r"D:\Research\vol 2\credentials\google_credentials.json",
    scopes=SCOPES
)

client = gspread.authorize(creds)

spreadsheet = client.open_by_key(
    "1dbdTY8QeFL5p1bDVDjBalMx_UjRejrP3MpYZOVVqVcE"
)

print(spreadsheet.title)

worksheet = spreadsheet.worksheet("Summary")

print(worksheet.title)

headers = worksheet.row_values(1)

print(headers)

worksheet.append_row([
    "TEST001",
    "2026-07-29 21:30",
    "TC001",
    "Llama3.2",
    "P001",
    "Appendicitis",
    "Completed",
    "No",
    0,
    0.95,
    2.13
])
