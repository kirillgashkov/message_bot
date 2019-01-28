"""
Bot engine based on social-networking site VK.
"""

import json
from typing import Optional, Tuple, Callable

from vk_api import vk_api, longpoll

from message_bot import bot, models, container
from message_bot.constants import VK_API_CREDS, HELP_OFFER_ON_ERROR


class VKEngine(bot.engines.BaseEngine):

    def __init__(self):
        username, password = credentials()
        self.vk_session = vk_session(username, password)
        self.vk_api = self.vk_session.get_api()

    def message(self, person: models.Person, m: str):
        identifier = person.ids.get('vk')
        if not identifier:
            print("MessageBotError: targeted person doesn't have vk id.")
            return
        self.vk_api.messages.send(user_ids=identifier, message=m)

    def error(self, person: models.Person, m: str, e: Optional[Exception]):
        identifier = person.ids.get('vk')
        if not identifier:
            print("MessageBotError: targeted person doesn't have vk id.")
            return
        s = f'{m} {HELP_OFFER_ON_ERROR}'
        self.vk_api.messages.send(user_ids=identifier, message=s)

    def run(self, message_handler: Callable[[models.Person, str], None]):
        vk_longpoll = longpoll.VkLongPoll(self.vk_session)
        for event in vk_longpoll.listen():
            is_new_message = event.type != longpoll.VkEventType.MESSAGE_NEW
            is_from_user = event.from_user
            if not is_new_message or not is_from_user:
                continue
            person = container.person_for_id('vk', event.user_id)
            message = event.text
            message_handler(person, message)


#
# Utilities
#


def vk_session(username: str, password: str) -> Optional[vk_api.VkApi]:
    session = vk_api.VkApi(username, password)
    try:
        session.auth(token_only=True)
    except vk_api.AuthError as e:
        print(e)
        return None
    return session


def credentials() -> Tuple[str, str]:
    creds = json.load(VK_API_CREDS)
    return creds['username'], creds['password']
