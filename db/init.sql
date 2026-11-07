-- Таблицы создаются при первом старте контейнера. Hibernate (ddl-auto=update) совместим с этой схемой.
-- UNIQUE (title, date) нужен для идемпотентной загрузки: INSERT ... ON CONFLICT DO NOTHING.
CREATE TABLE IF NOT EXISTS events (
    id              BIGSERIAL PRIMARY KEY,
    title           TEXT,
    date            TIMESTAMP,
    genre           TEXT,
    age_restriction TEXT,
    location        TEXT,
    details         TEXT,
    scene           TEXT,
    CONSTRAINT events_title_date_uniq UNIQUE (title, date)
);

CREATE TABLE IF NOT EXISTS geolocation (
    id            BIGSERIAL PRIMARY KEY,
    location_name TEXT NOT NULL,
    address       TEXT NOT NULL,
    longitude     DOUBLE PRECISION NOT NULL,
    latitude      DOUBLE PRECISION NOT NULL
);
