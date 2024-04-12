import socket
import struct
import sys

# Acessando os argumentos passados
argumentos = sys.argv


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



def getFile (filename , client):
    data, addr = client.recvfrom(1500)
    if data.decode("utf-8") == "Arquivo não encontrado":
        print ("Arquivo não encontrado")
        return
    print (f"Server: arquivo {filename} encontrado")
    with open(f"client/arquivos/{filename}", "w",encoding='utf-8') as file:
        i = 1
        while True:
            data, addr = client.recvfrom(1026)
            
            # Verificando o checksum
            checksum = struct.unpack("H", data[:2])[0] 
            data = data[2:]
            # Verificando se é o fim do arquivo
            if data.decode("utf-8") == "EOF":
                break
            calculated_checksum = calculate_checksum(data)

            if checksum == calculated_checksum:
                print("Checksum válido")
                file.write(data.decode("utf-8"))
                client.sendto(f'ACK {i}'.encode("utf-8"), addr)
            else:
                print("Checksum inválido")
                break
            i += 1
        print (f"Server: arquivo {filename} recebido com sucesso")


def main():
    host = "127.0.0.1"
    port = 4455 
    addr = (host, port)

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


    while True:
        comand = input("Enter a word: ")

        data = comand.encode("utf-8")
        client.sendto(data, addr)
        
        comand = comand.split(" ")
        if(comand[0] == "GET" and comand.__len__() > 1):
           getFile(comand[1], client)
        else:
            data,addr = client.recvfrom(1024)
            print (data.decode("utf-8"))
            print (addr)
        

if __name__ == "__main__":
    main()
