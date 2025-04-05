import json
import requests
from bs4 import BeautifulSoup
import os

pass_dict = json.loads(os.environ['pass_dict'])
print("共{}位".format(len(pass_dict)))

headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://www.ablesci.com",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://www.ablesci.com/site/login",
    "sec-ch-ua": "\"Chromium\";v=\"134\", \"Not:A-Brand\";v=\"24\", \"Google Chrome\";v=\"134\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest"
}
url = "https://www.ablesci.com/site/login"
def get_csrf():
    response = requests.get(url, headers=headers)
    try:
        return json.loads(response.text)['data']['csrf']
    except json.decoder.JSONDecodeError:
        soup = BeautifulSoup(response.text, 'lxml')
        csrf = soup.find(id='csrf-val')
        print("---csrf:" + csrf.get('value') + "---")
        return csrf.get('value')
def get_cookies(username, password):
    data = {
        "_csrf": get_csrf(),
        "email": username,
        "password": password,
        "remember": "on"
    }
    response_cookie = requests.post(url, headers=headers, data=data)
    return response_cookie.cookies
def get_main_html():
    header = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    }
    url = "http://www.ablesci.com/"
    requests.get(url, headers=header)
    response2 = requests.get(url, headers=headers, cookies=Cookie)
    print(response2.text)

def get_sign():
    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "zh-CN,zh;q=0.9",
        "priority": "u=1, i",
        "referer": "https://www.ablesci.com/",
        "sec-ch-ua": "\"Chromium\";v=\"134\", \"Not:A-Brand\";v=\"24\", \"Google Chrome\";v=\"134\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest"
    }
    url = "https://www.ablesci.com/user/sign"
    response = requests.get(url, headers=headers, cookies=Cookie)

    print(response.text)
    print(response)

for username in pass_dict:
    password = pass_dict[username]
    Cookie = get_cookies(username, password)
    get_sign()
