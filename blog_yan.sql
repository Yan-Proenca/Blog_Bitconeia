CREATE DATABASE blog_yan;
USE blog_yan;

CREATE TABLE usuario (
    idUsuario INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(70) NOT NULL,
    user VARCHAR(15) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    foto VARCHAR(100),
    ativo BOOLEAN NOT NULL DEFAULT 1,
    dataCadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE post (
    idPost INT PRIMARY KEY AUTO_INCREMENT,
    titulo VARCHAR(50) NOT NULL,
    conteudo TEXT NOT NULL,
    dataPost TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    idUsuario INT NOT NULL,
    FOREIGN KEY (idUsuario)
        REFERENCES usuario(idUsuario)
        ON DELETE CASCADE
);
