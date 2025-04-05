import pandas
import json
import pyperclip
try:
    password_dict = {}
    sheet = pandas.read_excel("password.xlsx",  header = 0)
    for row in sheet.iterrows():
        print(row[1][0]+":"+row[1][1])
        print('---------------')
        password_dict[row[1][0]] = row[1][1]
    text = json.dumps(password_dict)
    pyperclip.copy(text)
except Exception as e:
    print(e)
