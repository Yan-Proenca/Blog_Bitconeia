SECRET_KEY = "Bl0gy4(\)!"     # senha secreta para sessão e outras coisas
USUARIO_ADMIN = "yanproenca.senai@gmail.com"        # senha do adm (alterar para uma mais segura
SENHA_ADMIN = "Yan38t40"          # senha do adm (alterar para uma mais segura

# Variável de controle de ambiente, poderá ser "local" ou "produção"
ambiente = "local"

if ambiente == "local":
	# ------ INFORMAÇÕES DO SEU BLOG LOCAL, DEIXE COMO ESTÁ
	HOST = "localhost"
	USER = "root"
	PASSWORD = "senai"
	DATABASE = "blog_yan"
elif ambiente == "produção":
	# ------ INFORMAÇÕES VINDAS DO DATABASE DO PYTHON ANYWHERE
	HOST =  "YanMatheus.mysql.pythonanywhere-services.com"
	USER = "YanMatheus"
	PASSWORD = "Y4nPIth0N74n#wh3r"
	DATABASE = "YanMatheus$default"