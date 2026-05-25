CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    login VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL
);

CREATE TABLE IF NOT EXISTS refresh_tokens (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    token_hash VARCHAR(512) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_revoked BOOLEAN DEFAULT FALSE,

    CONSTRAINT fk_refresh_tokens_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
CREATE INDEX idx_refresh_tokens_is_revoked ON refresh_tokens(is_revoked);

CREATE TABLE IF NOT EXISTS user_folders (
    id SERIAL PRIMARY KEY,
    idUser INT NOT NULL,
    folder_name VARCHAR(255) NOT NULL,

    CONSTRAINT fk_user_folders_login
        FOREIGN KEY (idUser)
        REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS uploaded_files (
    id SERIAL PRIMARY KEY,
    idUser INT NOT NULL,
    folder_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(1024) NOT NULL,

    CONSTRAINT fk_uploaded_files_login
        FOREIGN KEY (idUser)
        REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ParserType (
    universityName  VARCHAR(255) PRIMARY KEY,
    parserType  INT NOT NULL
);

CREATE TABLE IF NOT EXISTS comparedGraphs (
    hash VARCHAR(1024) PRIMARY KEY,
    id_user INT NOT NULL,
    program_name VARCHAR(255) NOT NULL,
    compared_with_programs VARCHAR(255)[] NOT NULL,
    recommendations VARCHAR(1024)[] NOT NULL
);