import time

import requests
from bs4 import BeautifulSoup
from loguru import logger

from config import URL, BOT_ID, CHAT_ID
from telegram import Telegram


class Damages:
    def __init__(self, url, bot_id, chat_id):
        self.url = url
        self.telegram = Telegram(bot_id, chat_id)
        self.damages = dict()

    def get_damages(self) -> dict:
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", {"class": "table table-bordered table-sm table-responsive-md"})
        if not table:
            logger.debug("Нет отключений")
            return {}

        current_damages = dict()
        for row in table.findAll("tr"):
            aux = row.findAll("td")
            if not aux:
                continue
            current_damages[aux[7].get_text()] = {
                "addresses": aux[0].get_text(),
                "disabled": aux[1].get_text(),
                "cause": aux[2].get_text(),
                "when_disabled": aux[3].get_text(),
                "plan_time": aux[4].get_text(),
                "organization": aux[5].get_text(),
                "phone": aux[6].get_text(),
            }
        return current_damages

    def update_damages(self):
        try:
            current_damages = self.get_damages()
        except Exception as e:
            logger.error(e)
            time.sleep(3600)
            return

        for id_ in set(self.damages.keys()) - set(current_damages.keys()):
            logger.info(f"End damage {id_}")
            del self.damages[id_]
            self.send_alert("end", self.damages[id_])

        for id_, damage in current_damages.items():
            if id_ not in self.damages:
                status = "new"
            elif damage != self.damages[id_]:
                status = "change"
            else:
                continue
            logger.info(f"{id_}: status {status} ")
            self.damages[id_] = damage
            self.send_alert(status, damage)

    def send_alert(self, status, damage_data):
        logger.debug(f"{status} :{damage_data}")
        if status == "new":
            msg = "Новая авария"
        elif status == "change":
            msg = "Изменение данных об аварии"
        elif status == "end":
            msg = "Авария окончена"
        else:
            msg = {status}

        msg += f"""
Авария по адресу: {damage_data["addresses"]}
Отключено: {damage_data["disabled"]}
Причина: {damage_data["cause"]}
Когда отключено: {damage_data["when_disabled"]}
План. время включения: {damage_data["plan_time"]}
Ответств. организация: {damage_data["organization"]}
Телефон: {damage_data["phone"]}"""

        self.telegram.send_message(msg)


if __name__ == "__main__":
    damages = Damages(URL, BOT_ID, CHAT_ID)
    while True:
        logger.info("Update damages info")
        damages.update_damages()
        time.sleep(300)
