import socket
import struct
import os as cv2




#O processo para a exeucação do servidor é o seguinte:
# irá receber uma mensagem do cliente , com o seguinte formato "GET ./<nome do arquivo>"
# o servidor irá verificar se o arquivo existe, caso exista ele irá enviar o arquivo para o cliente
# caso não exista ele irá enviar uma mensagem de erro para o cliente
# Então ele irá pegar o arquivo e enviar para o cliente no formato de segmentos de um tamanho fixo
# Para cada segmento tem que haver um reconhecimento do cliente, caso não haja o servidor irá reenviar o segmento

import hashlib

# Função para calcular o checksum dos dados
def calculate_checksum(data):
    sum = 0
    for i in range(0, len(data), 2):
        if i + 1 < len(data):
            word = (data[i] + (data[i + 1] << 8))
        elif i < len(data):
            word = data[i]
        sum += word
        sum = (sum & 0xffff) + (sum >> 16)
    checksum = (~sum & 0xffff)
    return checksum  

def addChecksum(data):  
    checksum = calculate_checksum(data)
    header_format = "H"
    header_with_checksum = struct.pack(header_format, checksum)
    return header_with_checksum + data

def getFile (filename):
    try:
        file = open(f"server/arquivos/{filename}", "rb")
        return file.read()
    except FileNotFoundError:
        return "Arquivo não encontrado"


def sendFile( file, addr, server):
    segment_size = 1024
    segments = [file[i:i+segment_size] for i in range(0, len(file), segment_size)]
    for segment in segments:
        data = addChecksum(segment)
        print("Enviando segmento")
        server.sendto(data, addr)
        ack, addr = server.recvfrom(1024)
        print(ack.decode("utf-8"))
        if ack.decode("utf-8") != f"ACK {segments.index(segment) + 1}":
            print("Erro no envio do segmento")
            message_EOF = "EOF"
            message = addChecksum(message_EOF.encode("utf-8"))
            server.sendto(message, addr)
            break
        else:
            print("Segmento enviado com sucesso")
    message_EOF = "EOF"
    message = addChecksum(message_EOF.encode("utf-8"))
    server.sendto(message, addr)
    

def main():
    host = "127.0.0.1"
    port = 4455 

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server.bind((host, port))

    while True:
        data, addr = server.recvfrom(1024)
        print("Recebendo de ", addr, " : ", data)
        data = data.decode("utf-8")
        data = data.split(" ")
        if(data.__len__() < 2 or data[0] != "GET"):
            print ("Comando inválido")
            server.sendto("Comando inválido".encode("utf-8"), addr)
            continue
        if(data[0] == "GET"):
            file = getFile(data[1])
            if(file == "Arquivo não encontrado"):
                server.sendto(file.encode("utf-8"), addr)
                continue
            server.sendto("Arquvo encontrado".encode("utf-8"), addr)
            sendFile(file, addr, server)


if __name__ == "__main__":
    main()