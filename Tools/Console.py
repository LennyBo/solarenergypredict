from datetime import datetime


def log(message):
    print(f'{datetime.now().strftime("%Y-%M-%d %H:%M")} - {message}')
