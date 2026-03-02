CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    login VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL
);

CREATE TABLE user_folders (
    id SERIAL PRIMARY KEY,
    login VARCHAR(50) NOT NULL,
    folder_name VARCHAR(255) NOT NULL,

    CONSTRAINT fk_user_folders_login
        FOREIGN KEY (login)
        REFERENCES users(login)
        ON DELETE CASCADE
);

CREATE TABLE uploaded_files (
    id SERIAL PRIMARY KEY,
    login VARCHAR(50) NOT NULL,
    folder_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(1024) NOT NULL,

    CONSTRAINT fk_uploaded_files_login
        FOREIGN KEY (login)
        REFERENCES users(login)
        ON DELETE CASCADE
);