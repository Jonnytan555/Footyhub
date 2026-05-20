-- PostgreSQL schema for FootyhubAws
-- Run this against your RDS instance to create all tables

CREATE TABLE articles (
    id               SERIAL PRIMARY KEY,
    source_type      VARCHAR(100)  NOT NULL,
    source_name      VARCHAR(200)  NOT NULL,
    source_record_id VARCHAR(500)  NOT NULL,
    source_url       VARCHAR(1000),
    title            VARCHAR(500),
    body_text        TEXT,
    published_at     VARCHAR(20),
    topic            VARCHAR(100),
    competition      VARCHAR(100),
    club             VARCHAR(200),
    player_name      VARCHAR(200),
    theme            VARCHAR(100),
    clubs_mentioned  VARCHAR(500),
    players_mentioned VARCHAR(500),
    created_at       TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_articles UNIQUE (source_type, source_name, source_record_id)
);

CREATE TABLE article_queue (
    id               SERIAL PRIMARY KEY,
    source_type      VARCHAR(100)  NOT NULL,
    source_name      VARCHAR(200)  NOT NULL,
    source_record_id VARCHAR(500)  NOT NULL,
    source_url       VARCHAR(1000),
    title            VARCHAR(500),
    body_text        TEXT,
    published_at     VARCHAR(20),
    topic            VARCHAR(100),
    status           VARCHAR(50)   NOT NULL DEFAULT 'pending',
    created_at       TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_article_queue UNIQUE (source_type, source_name, source_record_id)
);

CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    favourite_club VARCHAR(200),
    created_at    TIMESTAMP DEFAULT NOW()
);

CREATE TABLE article_likes (
    user_id    INT NOT NULL,
    article_id INT NOT NULL,
    PRIMARY KEY (user_id, article_id)
);

CREATE TABLE chat_messages (
    id         SERIAL PRIMARY KEY,
    user_id    INT NOT NULL,
    role       VARCHAR(20)  NOT NULL,
    content    TEXT         NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
