import socket
import struct
import os as cv2

TIMEOUT = 2


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

def addNumberSegment(data, number):
    header_format = "H"
    header_with_number = struct.pack(header_format, number)
    return header_with_number + data

def createPackage(data, number):
    data = addChecksum(data)
    data = addNumberSegment(data, number)
    return data

def getFile (filename):
    try:
        file = open(f"server/arquivos/{filename}", "rb")
        return file.read()
    except FileNotFoundError:
        return "Arquivo não encontrado"



def sendFile( file, addr, server):
    segment_size = 1024
    segments = [file[i:i+segment_size] for i in range(0, len(file), segment_size)]
    server.settimeout(TIMEOUT)
    i = 0
    while i < len(segments):
        package = createPackage(segments[i], i)
        print("Enviando segmento ", i) 
        server.sendto(package, addr)
        try:
            message, addr = server.recvfrom(1024)
        except socket.timeout:
            print("Timeout")
            continue 
        message = message.decode("utf-8").split(" ")
        numberACK = int(message[1])
        print("Recebendo ACK", numberACK)
        if numberACK < i:
            print("Erro no envio do segmento")
            i = numberACK + 1
            continue
        elif message :
            print("Segmento enviado com sucesso")
        i += 1 
    
    print("Mandando EOF")
    package = createPackage("EOF".encode("utf-8"), 0)
    server.sendto(package, addr)


    try:
        while True:
            message, addr = server.recvfrom(1024)
            print("message: ",message.decode("utf-8"))
            message = message.decode("utf-8").split(" ")
            if message[0] == "RECEBIDO":
                break
        
    except socket.timeout:
        print("Timeout, Deu RUIM")
        return
    print("Arquivo enviado com sucesso")
    

def main():
    host = "127.0.0.1"
    port = 4455 
    
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    

    server.bind((host, port))

    while True:
        server.settimeout(None)
        data, addr = server.recvfrom(1024)
        print("Recebendo de ", addr, " : ", data)
        data = data.decode("utf-8")
        if(data == "exit"):
            server.sendto("exit".encode("utf-8"), addr)
            break
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

    server.close()


if __name__ == "__main__":
    main()