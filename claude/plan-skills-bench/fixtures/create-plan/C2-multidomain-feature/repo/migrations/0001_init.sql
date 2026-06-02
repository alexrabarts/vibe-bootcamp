CREATE TABLE users (
    id    TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE dashboards (
    id      TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    name    TEXT NOT NULL
);

-- No table for saved filters yet.
