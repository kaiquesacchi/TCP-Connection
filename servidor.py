import socket
import sys
import os.path
import threading


def main():
	# Definição do ip e porta de conexão ______________________________________
	if len(sys.argv) != 2:
		print("Uso do programa: python3 servidor.py <porta>")
		exit(1)

	server = "localhost"
	port = int(sys.argv[1])

	# Criação do socket _______________________________________________________
	print("[PRINCIPAL] Iniciando servidor em {}:{}".format(server, port))
	tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	tcp.bind((server, port))

	# Começa a escutar novas conexões. Limitado a 10 simultâneas
	tcp.listen(10)

	while (True):
		print("[PRINCIPAL] Aguardando conexão")
		print("[PRINCIPAL] Threads ativas: " + str(threading.active_count()))
		connection, client_address = tcp.accept()
		new_client = threading.Thread(
			group=None, target=client_thread, name=None,
			args=(connection, client_address), kwargs={}, daemon=None
		)
		new_client.start()
		print("[PRINCIPAL] Thread criada para lidar com requisição")


def client_thread(connection, client_address):
	try:
		print("[THREAD {}] Conectado a {}".format(
			threading.get_ident(), client_address
		))

		# Começa um buffer
		data = connection.recv(4).decode('utf-8')
		if   data == "GET ": get(connection, data)
		elif data == "PUT ": put(connection, data)
		else               : text(connection, data)

	finally:
		connection.close()
		print("[THREAD {}] Conexão fechada".format(threading.get_ident()))


# Funções Auxiliares __________________________________________________________

def get(connection, data):
	# Leitura do nome do arquivo
	data = connection.recv(256).decode('utf-8')
	if len(connection.recv(1)) != 0:
		connection.send(
			"ERROR 2 - Nome muito longo (max. 256 caracteres".encode())
		return

	# Checa se arquivo existe
	if not os.path.isfile(data):
		return connection.send("ERROR 1 - Arquivo não existe".encode())

	# Transmissão do arquivo
	with open(data, "r") as file:
		message = file.read()
		connection.send(("size: " + str(os.path.getsize(data)) +
			"\r\n" + message).encode())


def put(connection, data):
	data = connection.recv(256).decode('utf-8')

	with open(data.split(" ", 1)[0], "w") as file:
		data = data.split("\r\n", 1)[1]
		while len(data) != 0:
			file.write(data)
			data = connection.recv(4096).decode('utf-8')

	return "PUT recebido"


def text(connection, data):
	while len(data) != 0:
		print(data)
		data = connection.recv(1024).decode('utf-8')
	return "Mensagem recebida"


main()
