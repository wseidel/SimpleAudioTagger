PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE wav_data (
    wav_file TEXT PRIMARY KEY,
    palavra TEXT,
    falado TEXT,
    tipo TEXT,
    is_error INTEGER,
    docid TEXT
);

CREATE TABLE user_choices (
    wav_file TEXT,
    username TEXT,
    user_choice TEXT,
    UNIQUE (wav_file, username)  -- Define uma restrição UNIQUE nas colunas wav_file e username
);


CREATE TABLE wav_file_to_check (
    filter TEXT,
    wav_file TEXT,
    UNIQUE (wav_file, filter)
);

COMMIT;
