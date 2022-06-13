import requests
import os

def send_message(text,token, chat_id):
    url = f"https://api.telegram.org/bot{token}"
    params = {"chat_id": chat_id, "text": text}
    r = requests.get(url + "/sendMessage", params=params)
    return r

def easy_message(text):
    r = send_message(text, os.environ.get("TELEGRAM_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID"))
    return r

if __name__=="__main__":
    print(easy_message("Hello World!").text)