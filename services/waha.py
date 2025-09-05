import requests

from core.exceptions import (
    ConfigurationException,
    WahaException
)
from core.config import Config


class Waha:

    def __init__(self):
        try:
            self.__api_url = Config.WAHA_API_URL
            self.__session = Config.WAHA_SESSION

            if not self.__api_url:
                raise ConfigurationException("WAHA_API_URL is not configured")

            if not self.__session:
                raise ConfigurationException("WAHA_SESSION is not configured")

        except Exception as e:
            if isinstance(e, ConfigurationException):
                raise
            raise ConfigurationException(f"Error initializing WAHA client: {str(e)}")

    def send_message(self, chat_id: str, message: str):
        try:
            if not chat_id:
                raise WahaException("Chat ID cannot be empty")

            if not message:
                raise WahaException("Message cannot be empty")

        except WahaException:
            raise
        except Exception as e:
            raise WahaException(f"Error validating parameters: {str(e)}")

        try:
            url = f'{self.__api_url}/api/sendText'
            headers = {
                'Content-Type': 'application/json',
            }
            payload = {
                'session': self.__session,
                'chatId': chat_id,
                'text': message,
            }

            response = requests.post(
                url=url,
                json=payload,
                headers=headers,
                timeout=30
            )

            if not response.ok:
                raise WahaException(f"WAHA API error: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            raise WahaException(f"Network error sending message to {chat_id}: {str(e)}") from e
        except Exception as e:
            raise WahaException(f"Unexpected error sending message to {chat_id}: {str(e)}") from e

    def get_history_messages(self, chat_id: str, limit: int):
        try:
            if not chat_id:
                raise WahaException("Chat ID cannot be empty")

            if limit < 0:
                raise WahaException(f"Limit must be non-negative, got {limit}")

        except WahaException:
            raise
        except Exception as e:
            raise WahaException(f"Error validating parameters: {str(e)}")

        try:
            url = f'{self.__api_url}/api/{self.__session}/chats/{chat_id}/messages?limit={limit}&downloadMedia=false'
            headers = {
                'Content-Type': 'application/json',
            }

            response = requests.get(
                url=url,
                headers=headers,
                timeout=30
            )

            if not response.ok:
                raise WahaException(f"WAHA API error: {response.status_code} - {response.text}")

            return response.json()

        except requests.exceptions.RequestException as e:
            raise WahaException(f"Network error getting history for {chat_id}: {str(e)}") from e
        except Exception as e:
            raise WahaException(f"Unexpected error getting history for {chat_id}: {str(e)}") from e

    def start_typing(self, chat_id: str):
        try:
            if not chat_id:
                raise WahaException("Chat ID cannot be empty")

        except WahaException:
            raise
        except Exception as e:
            raise WahaException(f"Error validating chat_id: {str(e)}")

        try:
            url = f'{self.__api_url}/api/startTyping'
            headers = {
                'Content-Type': 'application/json',
            }
            payload = {
                'session': self.__session,
                'chatId': chat_id,
            }

            response = requests.post(
                url=url,
                json=payload,
                headers=headers,
                timeout=30
            )

            if not response.ok:
                raise WahaException(f"WAHA API error: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            raise WahaException(f"Network error starting typing for {chat_id}: {str(e)}") from e
        except Exception as e:
            raise WahaException(f"Unexpected error starting typing for {chat_id}: {str(e)}") from e

    def stop_typing(self, chat_id: str):
        try:
            if not chat_id:
                raise WahaException("Chat ID cannot be empty")

        except WahaException:
            raise
        except Exception as e:
            raise WahaException(f"Error validating chat_id: {str(e)}")

        try:
            url = f'{self.__api_url}/api/stopTyping'
            headers = {
                'Content-Type': 'application/json',
            }
            payload = {
                'session': self.__session,
                'chatId': chat_id,
            }

            response = requests.post(
                url=url,
                json=payload,
                headers=headers,
                timeout=30
            )

            if not response.ok:
                raise WahaException(f"WAHA API error: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            raise WahaException(f"Network error stopping typing for {chat_id}: {str(e)}") from e
        except Exception as e:
            raise WahaException(f"Unexpected error stopping typing for {chat_id}: {str(e)}") from e
