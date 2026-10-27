BEGIN TRANSACTION;

CREATE TABLE channel (
    id       INTEGER PRIMARY KEY,
    platform TEXT NOT NULL,
    login    TEXT NOT NULL,
    UNIQUE (platform, login)
) STRICT;

CREATE TABLE session (
    id         INTEGER PRIMARY KEY,
    channel_id INTEGER NOT NULL REFERENCES channel (id),
    started_at INTEGER NOT NULL,   -- Unix epoch ms, UTC
    ended_at   INTEGER             -- NULL while running
) STRICT;

CREATE TABLE message (
    id              INTEGER PRIMARY KEY,
    session_id      INTEGER NOT NULL REFERENCES session (id) ON DELETE CASCADE,
    platform_msg_id TEXT UNIQUE,
    sent_at         INTEGER NOT NULL,   -- Unix epoch ms, UTC
    user_login      TEXT NOT NULL,
    user_id         TEXT,
    display_name    TEXT NOT NULL,
    text            TEXT NOT NULL,
    emotes          TEXT NOT NULL DEFAULT '[]' CHECK (json_valid(emotes)),
    bits            INTEGER NOT NULL DEFAULT 0,
    is_broadcaster  INTEGER NOT NULL DEFAULT 0,
    is_mod          INTEGER NOT NULL DEFAULT 0,
    is_sub          INTEGER NOT NULL DEFAULT 0,
    is_first_msg    INTEGER NOT NULL DEFAULT 0,
    is_action       INTEGER NOT NULL DEFAULT 0,
    reply_to_msg_id TEXT,
    raw_line        TEXT NOT NULL
) STRICT;

CREATE INDEX ix_message_session_sent ON message (session_id, sent_at);
CREATE INDEX ix_message_user ON message (user_login);

COMMIT;