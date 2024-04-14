import socket
import struct
import sys
from time import sleep

# Acessando os argumentos passados
BUFFER  = 1500


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
    falha = True
    data, addr = client.recvfrom(BUFFER)
    if data.decode("utf-8") == "Arquivo não encontrado":
        print ("Arquivo não encontrado")
        return
    print (f"Server: arquivo {filename} encontrado")
    with open(f"client/arquivos/{filename}", "w",encoding='utf-8') as file:
        i = 0
        lastSegment = 0
        while True:
            print("Esperando segmento ", i)
            data, addr = client.recvfrom(BUFFER)
            if(i == 2 and falha == True):
                print("Descartei o segmento ", i)
                falha = False
                continue
            # Verificando o checksum
            numberPack = struct.unpack("H", data[:2])[0]
            checksum = struct.unpack("H", data[2:4])[0]
            data = data[4:]
            # Verificando se é o fim do arquivo

            if data.decode("utf-8") == "EOF":
                print("Fim do arquivo")
                client.sendto(f"RECEBIDO".encode("utf-8"), addr)
                break

            calculated_checksum = calculate_checksum(data)
            
            if checksum == calculated_checksum:
                print("Foi recebido o segmento ", numberPack , "esperado o segmento ", i)
                if(i != numberPack ):
                    print("Foi enviado o ACK anterior ", lastSegment )
                    client.sendto(f'ACK {lastSegment}'.encode("utf-8"), addr)
                    continue

                file.write(data.decode("utf-8"))
                print("Foi enviado o ACK ", i  )
                client.sendto(f'ACK {i}'.encode("utf-8"), addr)
                lastSegment = i
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
            data,addr = client.recvfrom(BUFFER)
            print (data.decode("utf-8"))
            print (addr)
        

if __name__ == "__main__":
    main()
