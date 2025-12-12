from flask import Flask, render_template, request, redirect, flash, session
from db import *
import mysql.connector
import os
from werkzeug.security import generate_password_hash, check_password_hash
from config import *  # importando o arquivo config.py


#Acessar as variáveis
secret_key = SECRET_KEY   # variáveis do arquivo config.py
usuario_admin = USUARIO_ADMIN  # variáveis do arquivo config.py
senha_admin = SENHA_ADMIN   # variáveis do arquivo config.py


#Informa o tipo do app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')
app.secret_key = secret_key #Chave secreta
#Configurar pasta de upload

# Rota da Página Inicial (Tudo que vem depois dos dominios)  
@app.route('/') 
def index():   # Chama função
    postagens = listar_post()
    return render_template('index.html', postagens=postagens)

#Rota do form de postagem
@app.route('/novopost', methods=['GET','POST'])
def novopost():
    # Bloquear admin de criar posts
    if 'admin' in session:
        flash("Administradores não podem criar posts")
        return redirect('/')
    
    if request.method == 'GET':
        return redirect('/')   
    else:
        titulo = request.form['titulo'].strip()
        conteudo = request.form['conteudo'].strip()
        idUsuario = session['idUsuario']
        
        if not titulo or not conteudo:
            flash("Preencha todos os campos!")
            return redirect('/')

        post = adicionar_post(titulo, conteudo, idUsuario)

        if post:
            flash("Post realizado com sucesso")
        else:
            flash("ERRO! Falha ao postar")
        return redirect('/')
    

    
#Rota para editar posts
@app.route('/editarpost/<int:idPost>', methods=['GET', 'POST'])
def editarpost(idPost):
    # Verificar se usuário está logado
    if 'user' not in session:
        return redirect('/login')
    
    # Bloquear admin de editar posts
    if 'admin' in session:
        flash("Administradores não podem editar posts")
        return redirect('/')
    
    with conectar() as conexao: 
        cursor = conexao.cursor(dictionary=True) 
        cursor.execute(f"SELECT * FROM post WHERE idPost = {idPost}")
        autor = cursor.fetchone() 
                                
        # Verificar se o usuário é o autor do post
        if not autor and autor['idUsuario'] != session.get('idUsuario'):
            print("Tentativa de edição indevida detectada")
            return redirect('/')
                
    
    
    if request.method == "GET":
        try:
            with conectar() as conexao: 
                cursor = conexao.cursor(dictionary=True) 
                cursor.execute(f"SELECT * FROM post WHERE idPost = {idPost}")
                post = cursor.fetchone() 
                                
                # Verificar se o usuário é o autor do post
                if post and post['idUsuario'] != session.get('idUsuario'):
                    flash("Você só pode editar seus próprios posts")
                    return redirect('/')
                
                postagens = listar_post()
                return render_template('index.html', postagens=postagens, post=post)
        except mysql.connector.Error as erro:
            print(f"ERRO NP BD! Erro {erro}")
        return []      
    
    # Método POST - Gravar edição
    if request.method == 'POST':
        # Verificar novamente se é o autor
        titulo = request.form['titulo'].strip()
        conteudo = request.form['conteudo'].strip()

        if not titulo or not conteudo:
            flash("Preencha todos os campos!")
            return redirect(f'/editarpost/{idPost}')
        
        try:
            with conectar() as conexao:
                cursor = conexao.cursor(dictionary=True)
                cursor.execute(f"SELECT idUsuario FROM post WHERE idPost = {idPost}")
                post = cursor.fetchone()

                
                
                if post and post['idUsuario'] != session.get('idUsuario'):
                    flash("Você só pode editar seus próprios posts")
                    return redirect('/')
                
                sucesso = atualizar_post(titulo, conteudo, idPost)

                if sucesso:
                    flash("Post atualizado com sucesso!")
                else:
                    flash("Erro ao atualizar post! Tente mais tarde.")
                return redirect('/')
        except mysql.connector.Error as erro:
            print(f"ERRO DO BD! Erro{erro}")
            flash("Ops! Tente mais tarde!")
            return redirect(f'/editarpost/{idPost}')
        

@app.route('/excluirpost/<int:idPost>')
def excluirpost(idPost):
    if 'user' not in session:  # Verificação mais específica
        print("Usuário não autorizado acessando rota para excluir")
        return redirect('/')
    
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            cursor.execute(f"SELECT idUsuario FROM post WHERE idPost = {idPost}")
            autor_post = cursor.fetchone()
            
            if not autor_post:
                flash("Post não encontrado")
                return redirect('/')
            
            # REGRA: Admin pode excluir QUALQUER post
            if 'admin' in session:
                cursor.execute(f"DELETE FROM post WHERE idPost = {idPost}") 
                conexao.commit()
                flash("Post excluído com sucesso pelo administrador!")

                if 'admin' in session:
                    return redirect('/dashboard')
                else:
                    return redirect('/')
            
            # REGRA: Usuário comum só pode excluir SEUS posts
            if autor_post['idUsuario'] == session.get('idUsuario'):
                cursor.execute(f"DELETE FROM post WHERE idPost = {idPost}") 
                conexao.commit()
                flash("Post excluído com sucesso!")
                return redirect('/')
            else:
                flash("Você só pode excluir seus próprios posts")
                return redirect('/')
                
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DO BD! Erro{erro}")
        flash("Ops! Tente mais tarde!")
        return redirect('/')





#Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    elif request.method == "POST":
        usuario = request.form['user'].lower().strip()
        senha = request.form['senha'].strip()

        if not usuario or not senha:
            flash("Preencha todos os campos!")
            return redirect('/login')
        
        # Verificar se é ADMIN
        if usuario == usuario_admin and senha == senha_admin:
            session['admin'] = True
            session['user'] = 'Administrador'
            session['idUsuario'] = 0  # ID especial para admin
            return redirect('/dashboard')
        
        # Verificar usuário comum
        resultado, usuario_encontrado = verificar_usuario(usuario, senha)


        
        if resultado:
            if usuario_encontrado['ativo'] == 0:
                flash("Usuário banido! Contate o administrador.")
                return redirect('/login')
            
            if usuario_encontrado['senha'] == '1234':
                session['idUsuario'] = usuario_encontrado['idUsuario']
                return render_template('novasenha.html')
            
            session['idUsuario'] = usuario_encontrado['idUsuario']
            session['user'] = usuario_encontrado['user']
            session['foto'] = usuario_encontrado['foto']
            flash(f"Bem-vindo, usuario_encontrado['nome']!")
            return redirect('/')
        
        # Se chegou aqui, credenciais inválidas
        flash("Usuário ou senha inválidos!")
        return redirect('/login')

        
        

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

#  Rota para cadastro de usuários
@app.route('/cadastro', methods=['GET','POST'])
def cadastro():
    if request.method == 'GET':
        return render_template('cadastro.html')

    elif request.method == 'POST':
        nome = request.form['nome'].strip()
        usuario = request.form['user'].lower().strip()
        senha = request.form['senha'].strip()

        if not nome or not usuario or not senha:
            flash('Preencha todos os campos!')
            return redirect('/cadastro')

        senha_hash = generate_password_hash(senha)
        foto = "placeholder.jpg"

        resultado, erro = adicionar_usuario(nome, usuario, senha_hash, foto)

        if resultado:
            flash("Usuário cadastrado com sucesso")
            return redirect('/login')

        else:
            if erro.errno == 1062:
                flash("Esse user já existe. Tente outro!")
                return redirect('/cadastro')
            else:
                flash("Erro ao cadastrar! Procure o suporte.")
                return redirect('/cadastro')  # <-- corrigido


@app.route('/usuario/status/<int:idUsuario>')
def status_usuario(idUsuario):
    if not session:
        return redirect('/')
    
    sucesso = alterar_status(idUsuario)

    if sucesso:
        flash("Status do usuário alterado com sucesso!")
    else:
        flash("Erro ao alterar status do usuário. Tente mais tarde!")

    return redirect('/dashboard')

#Área do ADM
@app.route('/dashboard')
def dashboard():
    #Bloqueio de acessos indevidos
    if not session or "admin" not in session:
        return redirect('/')
    
    usuarios = listar_usuario()
    posts = listar_post()
    total_posts, total_usuarios = totais()
    return render_template('dashboard.html', posts=posts, usuarios = usuarios, total_posts=total_posts, total_usuarios=total_usuarios)



@app.route('/usuario/excluir/<int:idUsuario>')
def delete_user(idUsuario):
    if "admin" not in session:
        return redirect('/')

    sucesso = delete_usuario(idUsuario)

    if sucesso:
        flash("Usuário excluído com sucesso!")
    else:
        flash("Erro ao excluir usuário. Tente mais tarde!")

    return redirect('/dashboard')

@app.route('/usuario/reset/<int:idUsuario>') #Quando nao tem nada, é metodo GET
def reset_senha_usuario(idUsuario):
    if "admin" not in session:
        return redirect('/')

    sucesso = reset_senha(idUsuario)

    if sucesso:
        flash(f"Senha do usuário redefinida para '1234' com sucesso!")
    else:
        flash("Erro ao redefinir senha. Tente mais tarde!")
    return redirect('/dashboard')

#Rota para salvar a nova senha
@app.route('/usuario/novasenha', methods=['GET','POST'])
def novasenha():
    if 'idUsuario' not in session:
        return redirect('/')
    
    if request.method == 'GET':
        return render_template('novasenha.html')
    
    if request.method == 'POST':
        senha = request.form['senha'].strip()
        confirmacao = request.form['confirma_senha'].strip()

        if not senha or not confirmacao:
            flash('Preencha corretamente a senha')
            return render_template('novasenha.html')
        if senha != confirmacao:
            flash('As senhas precisam ser iguais!')
            return render_template('novasenha.html')
        if senha == '1234':
            flash('A senha precisa ser alterada!')
            return render_template('novasenha.html')
        
        senha_hash = generate_password_hash(senha)
        idUsuario = session['idUsuario']
        sucesso = alterar_senha(senha_hash, idUsuario)
        if sucesso:
            flash("Senha alterada com sucesso!")
            if 'user' in session:
                return redirect('/perfil')
                
            return redirect('/login')
        else:
            flash('Erro no cadastro da nova senha!')
            return render_template('novasenha.html')
# Redirect vai para rota e processa tudo que vai na dentro
# O render abre o html no template, ele abre o template


@app.route('/perfil', methods=['GET','POST'])
def perfil():
    if 'user' not in session:
        return redirect('/')
    
    if request.method == 'GET':
        lista_usuarios = listar_usuario()
        usuario = None
        for u in lista_usuarios:
            if u['idUsuario'] == session['idUsuario']:
                usuario = u
                break
    
        return render_template('perfil.html', 
                            nome=usuario['nome'],
                            user=usuario['user'],
                            foto=usuario['foto'])
    
    if request.method == 'POST':
        nome = request.form['nome'].strip()
        user = request.form['user'].strip()
        foto = request.files['foto']
        idUsuario = session['idUsuario']
        nome_foto = None 

        if not nome or not user:
            flash("Os campos Nome e User não podem estar vazios!")
            return redirect('/perfil')
        
        if foto and foto.filename != '':
            extensao = foto.filename.rsplit('.', 1)[1].lower() 
            if extensao not in ['png', 'jpg', 'webp', 'jpeg']:
                flash("Extensão inválida. Use apenas PNG, JPG, JPEG ou WEBP")
                return redirect('/perfil')
            
            foto.seek(0, 2)  
            tamanho = foto.tell()  
            foto.seek(0)  
            if tamanho > 4 * 1024 * 1024:  
                flash("Arquivo acima de 4MB não é aceito")
                return redirect('/perfil')
            
            nome_foto = f"{nome}.{extensao}"
            
            try:
                # ✔ Trecho que você pediu
                caminho_completo = os.path.join(app.config['UPLOAD_FOLDER'], nome_foto)
                foto.save(caminho_completo)

            except Exception as e:
                print(f"❌ Erro ao salvar arquivo: {e}")
                flash("Erro ao salvar a imagem")
                return redirect('/perfil')
        else:
            lista_usuarios = listar_usuario()
            for u in lista_usuarios:
                if u['idUsuario'] == idUsuario:
                    nome_foto = u['foto']
                    break

        sucesso = editar_perfil(nome, user, nome_foto, idUsuario)
        
        if sucesso:
            session['user'] = user
            session['foto'] = nome_foto
            flash("Dados alterados com sucesso!")
            print("✅ Perfil atualizado no BD")
        else:
            flash("Erro ao alterar dados no banco")
            print("❌ Erro ao atualizar perfil no BD")
        
        return redirect('/perfil')




#ERRO 404
@app.errorhandler(404)
def pagina_nao_encontrada(e):
    return render_template("e404.html")

#ERRO 500
@app.errorhandler(500)
def erro_interno_do_servidor(e):
    return render_template("e500.html")  


# Executar App *Sempre no Final do código*
if __name__ == "__main__":
    app.run(debug=True)  # ,host="0.0.0.0" deixa público




#Operadora Ternario = __V__if_condição else__F___  "Maior de idade" if idade >=18 else "menor de idade"      
#TESTE jwp


#TESTE








