import gspread
import datetime
import os
import json

def connect_sheet():
    creds_path = "service_account.json"
    gc = gspread.service_account(filename=creds_path)
    sh = gc.open(os.getenv("GOOGLE_SHEET_NAME"))
    worksheet = sh.sheet1
    return worksheet

def save_contractor_report(user_id, date, name, job_type, unit, unit_price, quantity):
    sheet = connect_sheet()
    total = int(unit_price) * int(quantity)
    sheet.append_row([
        str(user_id),
        str(date),
        "کنترات",
        name,
        job_type,
        unit,
        unit_price,
        quantity,
        total
    ])

def save_worker_report(user_id, date, name, job_type, wage, overtime):
    sheet = connect_sheet()
    sheet.append_row([
        str(user_id),
        str(date),
        "روزمزد",
        name,
        job_type,
        wage,
        overtime
    ])
