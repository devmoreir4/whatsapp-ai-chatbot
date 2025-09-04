import requests
from decouple import config


class Waha:

    def __init__(self):
        self.__api_url = config('WAHA_API_URL', default='http://waha:3000')
        self.__session = config('WAHA_SESSION', default='default')

    def send_message(self, chat_id, message):
        url = f'{self.__api_url}/api/sendText'
        headers = {
            'Content-Type': 'application/json',
        }
        payload = {
            'session': self.__session,
            'chatId': chat_id,
            'text': message,
        }
        requests.post(
            url=url,
            json=payload,
            headers=headers,
        )

    def get_history_messages(self, chat_id, limit):
        url = f'{self.__api_url}/api/{self.__session}/chats/{chat_id}/messages?limit={limit}&downloadMedia=false'
        headers = {
            'Content-Type': 'application/json',
        }
        response = requests.get(
            url=url,
            headers=headers,
        )
        return response.json()

    def start_typing(self, chat_id):
        url = f'{self.__api_url}/api/startTyping'
        headers = {
            'Content-Type': 'application/json',
        }
        payload = {
            'session': self.__session,
            'chatId': chat_id,
        }
        requests.post(
            url=url,
            json=payload,
            headers=headers,
        )

    def stop_typing(self, chat_id):
        url = f'{self.__api_url}/api/stopTyping'
        headers = {
            'Content-Type': 'application/json',
        }
        payload = {
            'session': self.__session,
            'chatId': chat_id,
        }
        requests.post(
            url=url,
            json=payload,
            headers=headers,
        )
