CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY
)
CREATE TABLE IF NOT EXISTS guilds (
    id BIGINT PRIMARY KEY,
    inital_name VARCHAR(255), -- Most guilds change their name at least once --
    initial_owner BIGINT -- Just for commands like server info, in case of founder transfering or leaving the server --
)