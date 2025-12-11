CREATE DATABASE blog_yan;

USE blog_yan;

CREATE TABLE usuario (
    idUsuario INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(70) NOT NULL,
    user VARCHAR(15) NOT NULL UNIQUE,
    senha VARCHAR(355) NOT NULL,
    foto VARCHAR(100),
    dataCadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ativo BOOLEAN NOT FULL DEFAULT 1
);

CREATE TABLE post(
    idPost INT PRIMARY KEY AUTO_INCREMENT,
    titulo VARCHAR(50) NOT NULL,
    conteudo TEXT NOT NULL,
    dataPost TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    idUsuario int,
    FOREIGN KEY (idUsuario) REFERENCES usuario(idUsuario)
    ON DELETE CASCADE 
);

INSERT INTO usuario (nome, user, senha) VALUES 
('Yan Matheus Proenca Camargo', 'Yan Matheus', 'Teste543');

--Para zerar a tabela POST:
--TRUNCATE post;

--Cadastrar um usuario Teste:

-- 
-- DROP DATABASE IF EXISTS blog_yan;


ALTER TABLE usuario ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT 1;


alter table post add FOREIGN KEY (idUsuario) REFERENCES usuario(idUsuario) ON DELETE CASCADE;






CREATE VIEW vw_total_posts AS
SELECT COUNT(*) AS total_posts FROM post p
JOIN usuario u ON p.idUsuario = u.idUsuario
WHERE u.ativo = 1;

CREATE VIEW vw_usuarios AS
SELECT COUNT(*) AS total_usuarios
FROM usuario
WHERE ativo = 1;