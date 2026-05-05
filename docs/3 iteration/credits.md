# Как получить лицензию GraphDB

1. Необходимо перейти по [ссылке](https://www.ontotext.com/products/graphdb/?_gl=1*12346a7*_ga*MTAzODY2NzEwOC4xNzczMjY4MjMx*_ga_HGSKWBWCRK*czE3Nzc4MzA5NDEkbzgkZzEkdDE3Nzc4MzEwNTckajckbDAkaDA.#:~:text=Request%20GraphDB%20License)
2. Заполнить все поля и нажать на кнопку: Request license

<img width="1312" height="770" alt="image" src="https://github.com/user-attachments/assets/39a4d152-8d7b-4813-9818-94e8b499774e" />

3. Открыть указанную раннее почту и найти письмо следующего формата:

<img width="659" height="740" alt="image" src="https://github.com/user-attachments/assets/4b07dff8-b715-485d-a94f-615839603a86" />

4. В письме будет файл с лицензией, необходимо его скачать и переименовать в .rdf.license

После этого файл необходимо перенести в проект по пути: backend/src/rdf/.rdf.license

# Как получить доступ к llm GigaChat

1. Перейти по [ссылке](https://developers.sber.ru/studio/login)
2. Войти в аккаунт или создать его
3. Создать проект с нужным называнием и перейти в него
4. Перейти в настройки API
5. В этой вкладке будут ключи для доступа к API GigaChat
<img width="996" height="1016" alt="screenshot_1777994730" src="https://github.com/user-attachments/assets/818a1d45-76fa-430b-8f25-ba045f5381cf" />

## Для работы с сервисом необходимо выпустить два ssl сертификата. Один для авторизации, второй для запросов.
Для получения сертификатов необходимо выполнить следующие команды в терминале:
```
echo -n | openssl s_client -connect gigachat.devices.sberbank.ru:443 -servername gigachat.devices.sberbank.ru 2>/dev/null | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > Путь_до_папки_с_сертификатами/название_сертификата_для_запросов.pem
```
```
echo -n | openssl s_client -connect ngw.devices.sberbank.ru:9443 -servername ngw.devices.sberbank.ru 2>/dev/null | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > Путь_до_папки_с_сертификатами/название_сертификата_для_авторизации.pem
```
