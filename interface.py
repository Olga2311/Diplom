import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from config import comunity_token, acces_token
from core import VkTools
from data_store import adder


class BotInterface():

    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('Поиск', color=VkKeyboardColor.PRIMARY)

    def __init__(self, comunity_token, acces_token):
        self.interface = vk_api.VkApi(token=comunity_token)
        self.api = VkTools(acces_token)
        self.params = {}
        self.database = {}
        self.answer = ''

    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                              {'user_id': user_id,
                               'message': message,
                               'attachment': attachment,
                               'random_id': get_random_id(),
                               'keyboard': self.keyboard.get_keyboard()
                               }
                              )

    def get_city(self, params):
        longpoll = VkLongPoll(self.interface)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                self.answer = event.text.lower()
                if event.from_user:
                    city_title = self.answer.capitalize()
                    city_id = str(self.api.get_city_id(self.answer))
                    self.params['city'] = int(city_id)
                    break
        self.message_send(event.user_id, f'Будем искать в городе {city_title}')
        return params

    def get_bdate(self, params):
        longpoll = VkLongPoll(self.interface)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                answer = event.text.lower()
                if event.from_user:
                    self.params['bdate'] = answer.capitalize()
                    break
        return params

    def event_handler(self):
        longpoll = VkLongPoll(self.interface)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()
                if command == 'привет' or command == 'начать':
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'Приветствую тебя, {self.params["name"]}')
                    if not self.params.get('city') :
                        self.message_send(event.user_id,
                                          f' Введите название города для поиска, например: Москва'
                                          )
                        self.params = self.get_city(self.params)
                    if not self.params.get('bdate'):
                        self.message_send(event.user_id,
                                          f' Введите дату рождения в формате:"дд.мм.гггг"'
                                          )
                        self.params = self.get_bdate(self.params)
                elif command == 'поиск':
                    users = self.api.search_users(self.params)
                    if len(users) == 0:
                        users = self.api.search_users(self.params)
                        user = users.pop()
                    else:
                        user = users.pop()
                    attachment = ''
                    photos_user = self.api.get_photos(user['id'])
                    for num, photo in enumerate(photos_user):
                        attachment += f'photo{photo["owner_id"]}_{photo["id"]}'
                        if num == 2:
                            break
                    self.message_send(event.user_id,
                                      f'Встречайте {user["name"]} https://vk.com/id{user["id"]}',
                                      attachment=attachment
                                      )
                    """здесь логика для добавления в бд"""
                    profile_id = event.user_id
                    worksheet_id = user['id']
                    adder(profile_id, worksheet_id)
                elif command == 'пока':
                    self.message_send(event.user_id, 'До свидания!')
                else:
                    if command != self.answer:
                        self.message_send(event.user_id, 'Команда не опознана')



if __name__ == '__main__':
    bot = BotInterface(comunity_token, acces_token)
    bot.event_handler()
