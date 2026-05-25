# mse-template

## Запуск через Docker

### Требования
- Docker
- Docker Compose (плагин `docker compose`)

## Переменные окружения

Нужно создать файл `.env` в корне проекта, чтобы переопределить значения по умолчанию:

```env
APP_HOST=localhost
APP_PORT=8000

DB_MIN_CONN_NUMBER=5
DB_MAX_CONN_NUMBER=12
DB_HOST=localhost
DB_PORT=5432
DB_USER=danila
DB_PASSWORD=3484506
DB_NAME=universities

POSTGRES_DB=eduprogram
POSTGRES_USER=eduprogram
POSTGRES_PASSWORD=eduprogram_pass

GRAPHDB_HOST=localhost
GRAPHDB_PORT=7200
GRAPHDB_USER=admin
GRAPHDB_PASSWORD=root
GRAPHDB_REPOSITORY=universities

REACT_APP_API_URL=localhost:8000
REACT_APP_API_URL_ADD_PROGRAM=localhost:8000
REACT_APP_API_URL_GET_PROGRAMMS=localhost:8000

LOCAL_PATH_TO_STORAGE=./backend/src/storage

GIGACHAT_AUTH_URL=https://ngw.devices.sberbank.ru:9443/api/v2/oauth
GIGACHAT_QUERY_URL=https://gigachat.devices.sberbank.ru/api/v1/chat/completions
GIGACHAT_CLIEND_ID=id клиента после регистрации в гигачате
GIGACHAT_SCOPE=GIGACHAT_API_PERS
GIGACHAT_AUTHORIZATION_KEY=ключ авторизации после регистрации в гигачате
LEFT_LIMIT=0.4
RIGHT_LIMIT=0.6
USE_LLM=1
JWT_SECRET_KEY=4938hf39qpty812hfp93tg71pfgh1
```

Если `.env` не задан, `docker-compose.yml` использует безопасные значения по умолчанию.

### Быстрый старт
Из корня проекта выполните:

```bash
docker compose up --build -d
```

После запуска:
- Фронтенд: `http://localhost:3000`
- Бэкенд (FastAPI): `http://localhost:8000`
- PostgreSQL: внутри docker-сети (`db:5432`)
- GraphDB: `http://localhost:7200`

Остановить проект:

```bash
docker compose down
```

Остановить проект и удалить тома БД/хранилища:

```bash
docker compose down -v
```

## Dev-режим (hot-reload)


```bash
docker compose -f docker-compose.dev.yml up --build
```
Остановить dev-режим:

```bash
docker compose -f docker-compose.dev.yml down
```

## Проверка работоспособности
- Откройте `http://localhost:3000` и проверьте доступность интерфейса.
- Выполните регистрацию/вход через UI.
- Убедитесь, что запросы к API проходят на `http://localhost:8000`.

## Что добавлено для контейнеризации
- `docker-compose.yml` — оркестрация `frontend`, `backend`, `db`
- `docker-compose.dev.yml` — dev-режим с hot-reload для `frontend` и `backend`
- `backend/Dockerfile` — контейнер FastAPI
- `frontend/Dockerfile` + `frontend/nginx.conf` — production-сборка React и раздача через Nginx
- `.dockerignore` — ускорение сборки и уменьшение контекста
