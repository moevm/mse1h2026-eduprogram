from http import HTTPStatus
import requests
import uuid
from typing import Optional
import os
import time

class GigachatAPIError(Exception):
    pass

class GigachatAuthError(GigachatAPIError):
    pass

class GigachatQueryError(GigachatAPIError):
    pass


class GigachatService:
    def __init__(self, access_token: str = "", expires_at: int = 0):
        self.__access_token = access_token
        self.__expires_at = expires_at

    
    #метод получает токен для доступа к api посредством http запроса. данные сохраняются в приватные поля класса
    #если статус код не 200, выбрасывается ошибка
    def get_access_token (self)->None:
        url = os.getenv('GIGACHAT_AUTH_URL', "https://ngw.devices.sberbank.ru:9443/api/v2/oauth")
        client_id= os.getenv('GIGACHAT_CLIEND_ID', '')
        scope = os.getenv('GIGACHAT_SCOPE', 'GIGACHAT_API_PERS')
        authorization_key = os.getenv('GIGACHAT_AUTHORIZATION_KEY', '')
        cert_path = os.getenv('GIGACHAT_AUTH_CERT_PATH', '')

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'RqUID': str(uuid.uuid4()),
            'Authorization': f'Basic {authorization_key}'
        }
        
        payload = {
            'scope': scope,
            'client_id': client_id
        }

        response = requests.request("POST", url, headers=headers, data=payload, verify=cert_path)

        status_code = response.status_code
        try:
            response_data = response.json()
        except:
            response_data = {}

        if status_code == HTTPStatus.OK:
            self.__access_token = response_data.get('access_token')
            self.__expires_at = response_data.get('expires_at')
        elif status_code == HTTPStatus.BAD_REQUEST:
            raise GigachatAuthError(f"Статус код: {HTTPStatus.BAD_REQUEST}. Некорректный формат запроса");
        elif status_code == HTTPStatus.UNAUTHORIZED:
            raise GigachatAuthError(f"Код ошибки: {response_data.get('code')}. Текст ошибки: {response_data.get('message')}");

    #проверяет, истек ли срок токена
    def isExpired (self)->bool:
        time_ms = time.time() * 1000
        return True if time_ms > self.__expires_at else False

    #метод делает запрос с текстом, заданным в message. Если запрос возвращает 200, из метода вернется ответ, иначе выбросится ошибка
    def query(self, context: str, message: str, max_tokens: int)->str:
        if self.isExpired():
            try:
                self.get_access_token()
            except GigachatAuthError as ex:
                raise ex
        
        url = os.getenv('GIGACHAT_QUERY_URL', "https://gigachat.devices.sberbank.ru/api/v1/chat/completions")
        cert_path = os.getenv('GIGACHAT_QUERY_CERT_PATH', '')

        headers = {
            'Authorization': f'Bearer {self.__access_token}',
            'Content-Type': 'application/json'
        }

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": context
                },
                {
                    "role": "user",
                    "content": message
                }        
            ],
            "model": "GigaChat-2",
            "temperature": 0.87,
            "top_p": 0.47,
            "n": 1,
            "max_tokens": max_tokens,
            "repetition_penalty": 1.07,
            "stream": False,
            "update_interval": 0,
        }

        response = requests.post(url, headers=headers, json=payload, verify=cert_path)

        status_code = response.status_code

        try:
            response_data = response.json()
        except:
            response_data = {}

        if status_code == HTTPStatus.OK:
            return (response_data.get('choices', [{}])[0]
                                .get('message', {})
                                .get('content', ''))
        elif status_code == HTTPStatus.BAD_REQUEST:
            raise GigachatQueryError(f"Статус код: {HTTPStatus.BAD_REQUEST}. Некорректный формат запроса");
        else:
            raise GigachatQueryError(f"Статус код: {response_data.get('status')}. Текст ошибки: {response_data.get('message')}");