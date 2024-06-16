from os import getenv
from dotenv import load_dotenv


class Config:
    load_dotenv()

    db = getenv('database')
    token = getenv('token')
    interval_sending = int(getenv('interval_sending'))