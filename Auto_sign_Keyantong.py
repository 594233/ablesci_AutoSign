import asyncio
import json
import os
import random

import aiohttp
from bs4 import BeautifulSoup

LOGIN_URL = "https://www.ablesci.com/site/login"
SIGN_URL = "https://www.ablesci.com/user/sign"
ORIGIN = "https://www.ablesci.com"

pass_dict = json.loads(os.environ["pass_dict"])


def browser_headers(**extra):
    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": ORIGIN + "/",
        "sec-ch-ua": '"Google Chrome";v="134", "Not:A-Brand";v="24", "Chromium";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/134.0.0.0 Safari/537.36"
        ),
        "x-requested-with": "XMLHttpRequest",
    }
    headers.update(extra)
    return headers


def preview(text, limit=180):
    compact = " ".join((text or "").split())
    if len(compact) <= limit:
        return compact
    return compact[:limit] + "..."


def parse_json_body(text):
    try:
        return json.loads(text)
    except (TypeError, json.JSONDecodeError):
        return None


def is_already_signed(msg):
    text = msg or ""
    return "已" in text and "签到" in text and "今天" in text


def is_ok_code(code):
    return code in (0, "0")


def extract_csrf(text):
    payload = parse_json_body(text)
    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, dict) and data.get("csrf"):
            return "_csrf", data["csrf"]
        if payload.get("csrf"):
            return "_csrf", payload["csrf"]

    soup = BeautifulSoup(text, "html.parser")
    param = "_csrf"
    param_meta = soup.find("meta", attrs={"name": "csrf-param"})
    if param_meta and param_meta.get("content"):
        param = param_meta["content"]

    token_meta = soup.find("meta", attrs={"name": "csrf-token"})
    if token_meta and token_meta.get("content"):
        return param, token_meta["content"]

    hidden = soup.find("input", attrs={"name": param}) or soup.find(id="csrf-val")
    if hidden and hidden.get("value"):
        return param, hidden["value"]

    raise ValueError("login page has no csrf token")


async def read_response(response):
    text = await response.text()
    return response.status, text, parse_json_body(text)


async def request(session, method, url, **kwargs):
    async with session.request(
        method, url, allow_redirects=True, **kwargs
    ) as response:
        status, text, payload = await read_response(response)
        return status, text, payload


async def sign_one(username, password):
    await asyncio.sleep(random.uniform(0, 3))
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        status, login_page, _ = await request(
            session,
            "GET",
            LOGIN_URL,
            headers=browser_headers(referer=LOGIN_URL),
        )
        if status != 200:
            raise RuntimeError(
                "login page HTTP %s: %s" % (status, preview(login_page))
            )
        csrf_name, csrf = extract_csrf(login_page)

        data = {
            csrf_name: csrf,
            "email": username,
            "password": password,
            "remember": "on",
        }
        status, login_text, login_json = await request(
            session,
            "POST",
            LOGIN_URL,
            headers=browser_headers(
                referer=LOGIN_URL,
                origin=ORIGIN,
                **{"content-type": "application/x-www-form-urlencoded; charset=UTF-8"},
            ),
            data=data,
        )
        if status != 200:
            raise RuntimeError("login HTTP %s: %s" % (status, preview(login_text)))
        if login_json is not None:
            code = login_json.get("code")
            msg = login_json.get("msg") or preview(login_text)
            if not is_ok_code(code) and code is not None:
                raise RuntimeError("login failed: %s" % msg)
            print("%s login ok: %s" % (username, msg), flush=True)
        elif "退出" not in login_text:
            raise RuntimeError("login response is not json: %s" % preview(login_text))

        await asyncio.sleep(random.uniform(0, 3))
        status, sign_text, sign_json = await request(
            session, "GET", SIGN_URL, headers=browser_headers()
        )
        if status != 200:
            raise RuntimeError("sign HTTP %s: %s" % (status, preview(sign_text)))
        if sign_json is None:
            raise RuntimeError("sign response is not json: %s" % preview(sign_text))
        msg = sign_json.get("msg") or sign_text
        print("%s %s" % (username, msg), flush=True)
        if is_ok_code(sign_json.get("code")) or is_already_signed(msg):
            return
        raise RuntimeError("sign failed: %s" % msg)


async def main():
    if not isinstance(pass_dict, dict) or not pass_dict:
        raise SystemExit("pass_dict must be a non-empty JSON object")

    failed = []
    for username, password in pass_dict.items():
        try:
            await sign_one(username, password)
        except Exception as exc:
            failed.append(username)
            print("%s error: %s" % (username, exc), flush=True)

    if failed:
        raise SystemExit("failed accounts: %s" % ", ".join(failed))


if __name__ == "__main__":
    asyncio.run(main())
