import json
from bs4 import BeautifulSoup
import asyncio
import time
import aiohttp
import os

pass_dict = json.loads(os.environ['pass_dict'])

async def main(username, password):
    async with aiohttp.ClientSession() as session:
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
        async with await session.get(url, headers=headers) as response:
            try:
                csrf = json.loads(await response.text())['data']['csrf']
            except json.decoder.JSONDecodeError:
                soup = BeautifulSoup(await response.text(), 'lxml')
                csrf_inf = soup.find(id='csrf-val')
                # print("---csrf:" + csrf.get('value') + "---")
                csrf = csrf_inf.get('value')
        data = {
            "_csrf": csrf,
            "email": username,
            "password": password,
            "remember": "on"
        }
        async with await session.post(url, headers=headers, data=data) as response:
            Cookie = response.cookies
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
        async with await session.get(url, headers=headers, cookies=Cookie) as response:
            print(await response.text())

start = time.time()
tasks = []
for username in pass_dict:
    c = main(username, pass_dict[username])
    task = asyncio.ensure_future(c)
    tasks.append(task)
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait(tasks))

print(time.time()-start)
