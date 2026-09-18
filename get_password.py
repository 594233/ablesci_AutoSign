import json

import pandas
import pyperclip

try:
    sheet = pandas.read_excel("password.xlsx", header=0)
    accounts = sheet.iloc[:, :2].dropna(how="all")
    password_dict = {
        str(email).strip(): str(password)
        for email, password in accounts.itertuples(index=False, name=None)
        if str(email).strip() and str(email).lower() != "nan"
    }
    for email in password_dict:
        print("%s:******" % email)
        print("---------------")
    pyperclip.copy(json.dumps(password_dict, ensure_ascii=False))
    print("copied %d accounts to clipboard" % len(password_dict))
except Exception as exc:
    print(exc)
