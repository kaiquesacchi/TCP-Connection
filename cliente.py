import socket
import sys
import os.path


def main():
	# Definição do ip e porta de conexão
	if len(sys.argv) != 3:
		print("Uso do programa: python3 cliente.py <host> <porta>")
		exit(1)

	server = sys.argv[1]
	port = int(sys.argv[2])

	# Tradução do nome para endereço do servidor
	server_ip = socket.gethostbyname(server)

	# Criação do socket
	tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print("Conectando a {}:{}".format(server_ip, port))

	# Requisição
	tcp.connect((server, port))
	request   = input("Insira a Requisição               | ")

	if   request.startswith("GET"): get(tcp, request)
	elif request.startswith("PUT"): put(tcp, request)
	else: print("Função mal-formatada. Deve iniciar com GET ou PUT")
	tcp.close()


# _____________________________________________________________________________

def get(tcp, request):
	file = input("Insira o nome do arquivo de saída | ")

	# Envio da requisição
	tcp.send(request.encode())
	tcp.shutdown(socket.SHUT_WR)
	print("Mensagem enviada.")

	# Criação de um buffer para a recepção dos dados
	result = tcp.recv(4096).decode()
	if result.startswith("ERROR"):
		print("Houve um erro durante o processo da Requisição\n" + result)

	else:
		(size, data) = result.split("\r\n", 1)
		print(size)
		with open(file, 'w') as file:
			while len(data) != 0:
				file.write(data)
				data = tcp.recv(4096).decode('utf-8')


def put(tcp, request):
	# Checa se arquivo existe
	if not os.path.isfile(request[4:]):
		print("Arquivo não existe")
		return

	with open(request[4:], 'r') as file:
		request = request + " " + str(os.path.getsize(request[4:])) + \
			"\r\n" + file.read()
		print(request)

		# Envio da requisição
		tcp.send(request.encode())
		tcp.shutdown(socket.SHUT_WR)
		print("Mensagem enviada.")


main()
