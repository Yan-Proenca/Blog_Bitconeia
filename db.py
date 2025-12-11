import mysql.connector
from werkzeug.security import check_password_hash
from config import * # importando as variáveis do config.py
from werkzeug.security import generate_password_hash


# Função para se conectar ao Banco de Dados SQL
def conectar():
    conexao = mysql.connector.connect(
        host=HOST,   # variável do config.py
        user=USER,   # variável do config.py
        password=PASSWORD,   # variável do config.py
        database=DATABASE   # variável do config.py
    )
    if conexao.is_connected():
        print("Conexão com BD OK!")
    
    return conexao

#Função para listar todos os usuarios, traz elas para mim

def listar_usuario():
    try:
        with conectar() as conexao: #Faz a inicialização e a finalização, ele tipo porteiro --> conexao cria cursor
            cursor = conexao.cursor(dictionary=True) #Quando conectado ao BD, ele conecta e procura o que precisa
            cursor.execute("SELECT * FROM usuario")
            return cursor.fetchall() 
    except mysql.connector.Error as erro:
        print(f"ERRO NP BD! Erro {erro}")
        return []

#Função para listar todas as postagens, traz elas para mim
def listar_post():
    try:
        with conectar() as conexao: #Faz a inicialização e a finalização, ele tipo porteiro --> conexao cria cursor
            cursor = conexao.cursor(dictionary=True) #Quando conectado ao BD, ele conecta e procura o que precisa
            cursor.execute("SELECT p.*, u.user, u.foto FROM post p INNER JOIN usuario u ON u.idUsuario = p.idUsuario WHERE u.ativo = 1 ORDER BY idPost DESC")
            return cursor.fetchall() 
    except mysql.connector.Error as erro:
        print(f"ERRO NP BD! Erro {erro}")
        return []
    
def delete_usuario(idUsuario):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            sql = "DELETE FROM usuario WHERE idUsuario = %s"
            cursor.execute(sql, (idUsuario,))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DO BD! Erro{erro}")
        return False
    



def adicionar_post(titulo, conteudo, idUsuario):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            sql = "INSERT INTO post (titulo, conteudo, idUsuario) VALUES (%s, %s, %s)"
            cursor.execute(sql, (titulo, conteudo, idUsuario))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DO BD! Erro{erro}")
        return False
    
def adicionar_usuario(nome, usuario, senha, foto):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            sql = "INSERT INTO usuario (nome, user, senha, foto) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (nome, usuario, senha, foto))
            conexao.commit()
            return True, "ok"
    except mysql.connector.Error as erro:
        print(f"ERRO DO BD! Erro{erro}")
        return False, erro
    
def verificar_usuario(usuario, senha):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            sql = "SELECT * FROM usuario WHERE user = %s;"
            cursor.execute(sql, (usuario,)) # A virgula faz ser tupla
            usuario_encontrado = cursor.fetchone()
            if usuario_encontrado:
                if usuario_encontrado['senha'] == '1234' and senha == '1234':
                    return True, usuario_encontrado
                    # Devolvendo o código

                if check_password_hash(usuario_encontrado['senha'], senha):
                    return True, usuario_encontrado
            return False, None
    except mysql.connector.Error as erro:
        print(f"ERRO DO BD! Erro{erro}")
        return False, None
            

def alterar_status(idUsuario):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            sql = "SELECT ativo FROM usuario WHERE idUsuario = %s;"
            cursor.execute(sql, (idUsuario,))
            status = cursor.fetchone()

            if status['ativo']:
                sql = "UPDATE usuario SET ativo = 0 WHERE idUsuario = %s;"
            else:
                sql = "UPDATE usuario SET ativo = 1 WHERE idUsuario = %s;"

            cursor.execute(sql, (idUsuario,))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DO BD! Erro{erro}")
        return False

def atualizar_post( titulo, conteudo, idPost):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            sql = "UPDATE post SET titulo = %s, conteudo = %s WHERE idPost = %s;"
            cursor.execute(sql, (titulo, conteudo, idPost))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DO BD! Erro{erro}")
        return False
    

def totais():
    print("Entrou na função totais")
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM vw_total_posts")
            total_posts = cursor.fetchone()
            cursor.execute("SELECT * FROM vw_usuarios")
            total_usuarios = cursor.fetchone()
            print("Totais obtidos com sucesso com os valores:", total_posts, total_usuarios)
            return total_posts, total_usuarios
    except mysql.connector.Error as erro:
        print(f"ERRO NP BD! Erro {erro}")
        return None, None
    

def reset_senha(idUsuario):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            sql = "UPDATE usuario SET senha = '1234' WHERE idUsuario = %s;"
            cursor.execute(sql, (idUsuario,))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DO BD! Erro{erro}")
        return False  

def alterar_senha(senha_hash, idUsuario):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            sql = "UPDATE usuario SET senha = %s WHERE idUsuario = %s;"
            cursor.execute(sql, (senha_hash, idUsuario))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DO BD! Erro{erro}")
        return False  
    
def editar_perfil(nome, user, nome_foto, idUsuario):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            if nome_foto:
                sql = "UPDATE usuario SET nome = %s, user = %s, foto = %s WHERE idUsuario = %s;"
                cursor.execute(sql, (nome, user, nome_foto, idUsuario))
            else:
                sql = "UPDATE usuario SET nome = %s, user=%s WHERE idUsuario"
                cursor.execute(sql, (nome, user, nome_foto, idUsuario))

            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DO BD! Erro{erro}")
        return False