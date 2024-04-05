import socket
import os as cv2




#O processo para a exeucação do servidor é o seguinte:
# irá receber uma mensagem do cliente , com o seguinte formato "GET ./<nome do arquivo>"
# o servidor irá verificar se o arquivo existe, caso exista ele irá enviar o arquivo para o cliente
# caso não exista ele irá enviar uma mensagem de erro para o cliente
# Então ele irá pegar o arquivo e enviar para o cliente no formato de segmentos de um tamanho fixo
# Para cada segmento tem que haver um reconhecimento do cliente, caso não haja o servidor irá reenviar o segmento


def getFile (filename):
    try:
        file = open(filename, "rb")
        print (f"Arquivo {filename} encontrado")
        return file.read()
    except FileNotFoundError:
        return "Arquivo não encontrado"


def sendFile( file, addr, server):
    segment_size = 1024
    segments = [file[i:i+segment_size] for i in range(0, len(file), segment_size)]
    for segment in segments:
        server.sendto(segment, addr)
        ack, addr = server.recvfrom(1024)
        ack = ack.decode()
        if(ack != "ACK"):
            server.sendto(segment, addr)
    server.sendto("EOF".encode(), addr)
    print("Arquivo enviado com sucesso")

def main():
    host = "127.0.0.1"
    port = 4455 

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server.bind((host, port))

    while True:
        data, addr = server.recvfrom(1024)
        data = data.decode()
        print ("data: ", data)
        data = data.split(" ")
        file = ""
        if(data[0] == "GET"):
            file = getFile(data[1])
        #sendFile(file, addr, server)
        print (f"Client: {data}")

        #data = data.upper()
        #data = data.encode()
        server.sendto(data, addr)



if __name__ == "__main__":
    main()