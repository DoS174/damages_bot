import requests
from loguru import logger


class Telegram:
    def __init__(self, bot_id, chat_id):
        self.bot_id = bot_id
        self.chat_id = chat_id
        self.url = f"https://api.telegram.org/bot{self.bot_id}/sendMessage?chat_id={self.chat_id}&text="

    def send_message(self, msg):
        try:
            url = f"{self.url}{msg}"
            r = requests.get(url)
            if r.status_code != 200:
                logger.error(f"Ошибка отправки сообщения через telegram. status_code={r.status_code}")
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения через telegram {e}")
