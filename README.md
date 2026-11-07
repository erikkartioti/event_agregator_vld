# EventAgregator: агрегатор городских мероприятий с картой

Приложение собирает афиши театров Владикавказа, хранит их в PostgreSQL и показывает события на интерактивной карте.
Сбор и очистка данных выполняются по расписанию в **Apache Airflow**, источники опрашивает сервис **parser-api** на FastAPI,
а упавшие задачи разбирает **LLM-агент диагностики**.

## Стек

- **Backend:** Java 23, Spring Boot 3.4, Spring Data JPA, Thymeleaf
- **parser-api:** Python 3.12, FastAPI, Pydantic, requests, BeautifulSoup
- **ETL:** Apache Airflow 2.10 (LocalExecutor)
- **LLM-агент:** Anthropic API (tool use)
- **БД:** PostgreSQL 16 (отдельные базы для данных и для метаданных Airflow)
- **Карта:** OpenLayers, tileserver-gl
- **Инфраструктура:** Docker, Docker Compose

## Архитектура

```
Airflow DAG event_aggregator_etl (ежедневно, 16:00 МСК)
 ├─ extract_russian_theater ─┐   GET /sources/{name}/events
 ├─ extract_mariinsky ───────┴─> load_events ─> cleanup_outdated_events ─> assert_sources_healthy
 │                               (upsert ON CONFLICT)   (удаление прошедших)
 │  on_failure_callback
 ▼
parser-api (FastAPI) ──> источники: HTML-страницы | JSON API театров (адаптеры)
 └─ POST /diagnose ──> LLM-агент ──> probe_source / get_task_log / get_recent_runs ──> диагноз в логе задачи

PostgreSQL (events) <── Spring Boot (Controller → Service → Repository) ──> Thymeleaf-страницы /map, /database
```

## parser-api

| Метод | Путь | Назначение |
|---|---|---|
| GET | `/sources` | список источников (`html` или `api`) |
| GET | `/sources/{name}/events` | события источника в едином формате; 502 при сбое источника |
| GET | `/sources/{name}/probe` | диагностика источника: код ответа, наличие ожидаемой разметки или JSON |
| POST | `/diagnose` | диагноз упавшей задачи Airflow от LLM-агента |
| GET | `/health` | проверка работоспособности |

Документация OpenAPI: http://localhost:8000/docs

**Подключение настоящего API театра.** Публичного API у текущих двух сайтов не найдено, поэтому они разбираются как HTML.
Когда найдёте JSON-эндпоинт (вкладка Network в браузере или API билетной системы театра), добавьте источник без изменения кода:
скопируйте `api/sources.example.json` в `api/config/sources.json`, заполните URL и соответствие полей (`field_map`),
токены передавайте через `${ПЕРЕМЕННАЯ}` в заголовках, а в `.env` укажите `SOURCES_CONFIG=/config/sources.json`.
Затем добавьте имя нового источника в `SOURCES` в `airflow/dags/event_aggregator_etl.py`.

## LLM-агент диагностики

Когда задача DAG окончательно падает (после ретраев), Airflow вызывает `POST /diagnose`. Агент работает циклом с инструментами:

1. `probe_source`: открыт ли источник, какой код ответа, на месте ли разметка или JSON. Если страница отвечает 200, а ожидаемой разметки нет, это признак смены вёрстки.
2. `get_task_log`: хвост лога упавшей задачи.
3. `get_recent_runs`: повторяется ли сбой в последних запусках.
4. `submit_diagnosis`: структурированный итог (категория, причина, рекомендуемое действие, уверенность). Диагноз попадает в лог задачи.

Меры безопасности: инструменты только читают; аргументы проверяются по белому списку символов и реестру источников;
логи и страницы в промпте помечены как недоверенные данные; ограничен размер ответов инструментов и число шагов;
агент ходит в Airflow под отдельным пользователем с ролью Viewer; сбой диагностики не влияет на обработку сбоя задачи.
Агент ничего не чинит сам, он только объясняет и предлагает шаг инженеру.

## Запуск

```bash
cp .env.example .env      # задайте пароли и ANTHROPIC_API_KEY (ключ нужен только для /diagnose)
docker compose up --build
```

| Сервис | Адрес |
|---|---|
| Приложение | http://localhost:8090/map, http://localhost:8090/database |
| parser-api (Swagger) | http://localhost:8000/docs |
| Airflow UI | http://localhost:8080 (логин и пароль из `.env`) |
| Tileserver | http://localhost:9090 |

После запуска включите DAG `event_aggregator_etl` в интерфейсе Airflow или запустите его вручную.

## Тесты

```bash
cd api && python -m unittest discover -s tests -v          # парсеры, адаптеры, агент (с имитацией LLM), API
python -m unittest discover -s airflow/tests -v            # структура DAG (нужен установленный Airflow)
./mvnw test                                                # Spring Boot
```

## Известные ограничения

- Координаты на карте берутся из таблицы `geolocation`; связь событий с ней по названию площадки пока не реализована в бэкенде.
- Страницы отдаются через Thymeleaf; REST API есть только у parser-api.
- Spring-планировщики сохранены, но отключены в compose; пути к Python-скриптам в них относятся к локальной машине.


# WIP - миграция на React

# Перенос фронта на React + векторные тайлы + Qwen

## Структура
- `frontend/` — Vite + React + MapLibre GL (заменяет `static/main.js`, `map-fin.html`)
- `tiles/build_tiles.sh` — OSM → Tippecanoe → `vladikavkaz.mbtiles`
- `backend/assistant/` — 3 класса в пакет `...eventagregatornew.assistant`; свойства из `application.properties.additions`
- `docker-compose.additions.yml` — Martin (раздача mbtiles) и переменные Qwen

## Запуск
1. `cd tiles && ./build_tiles.sh <файл.osm.pbf>` → положить `vladikavkaz.mbtiles` в `tiles-data/`
2. `docker compose up tiles` (и Spring Boot как раньше)
3. `cd frontend && npm i && npm run dev` → http://localhost:5173
4. Задать `QWEN_API_KEY` (или `QWEN_BASE_URL` на локальный Ollama) и перезапустить бэкенд

## Прод
`npm run build`, содержимое `frontend/dist` положить в `src/main/resources/static`; `/tiles/*` проксировать на Martin (nginx).
