import socket
import struct
import sys
from time import sleep

# Acessando os argumentos passados
BUFFER  = 1030


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

def decodePackage(data):
    numberPack = struct.unpack("I", data[:4])[0]
    checksum = struct.unpack("H", data[4:6])[0]
    data = data[6:]
    return numberPack, checksum, data



def getFile (filename , client , indiceFalha):
    falha = True
    data, addr = client.recvfrom(BUFFER)
    data = decodePackage(data)
    if data[2].decode("utf-8") == "Arquivo não encontrado":
        print ("Arquivo não encontrado")
        return
    elif data[2].decode("utf-8") == "Arquivo encontrado":
        print (f"Server: arquivo {filename} encontrado")
    else:
        print("Erro ao receber o arquivo")
        return
    with open(f"client/arquivos/{filename}", "wb") as file:
        i = 1
        lastSegment = 0
        while True:
            data, addr = client.recvfrom(BUFFER)
            if(i == indiceFalha and falha == True):
                print("Descartei o segmento ", i)
                falha = False
                continue

            # Verificando o checksum
            numberPack, checksum, data = decodePackage(data)

            
            #Validando o checksum
            calculated_checksum = calculate_checksum(data)
            if checksum == calculated_checksum:
                #print("Foi recebido o segmento ", numberPack , "esperado o segmento ", i)
                if(i == numberPack):
                    file.write(data)
                    #print("Foi enviado o ACK ", i  )
                    client.sendto(f'ACK {i}'.encode("utf-8"), addr)
                    lastSegment = i
                    #print ("Esperado o segmento ", i, "recebido o segmento ", numberPack)
                elif(i != numberPack ):
                    #print ("Esperado o segmento ", i, "recebido o segmento ", numberPack)
                    if(numberPack == 0):
                        print("Fim do arquivo")
                        client.sendto(f"RECEBIDO".encode("utf-8"), addr)
                        break         
                    #print("Foi enviado o ACK anterior ", lastSegment )
                    client.sendto(f'ACK {lastSegment}'.encode("utf-8"), addr)
                    continue
                # Verificando se é o fim do arquivo
                
                
                
            else:
                print("Checksum inválido")
                break
            i += 1
        
        print (f"Server: arquivo {filename} recebido com sucesso")


def main():
    host = "127.0.0.1"
    port = 5555 
    addr = (host, port)

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


    while True:
        comand = input("Enter a word: ")

        data = comand.encode("utf-8")
        print (f"Client: Enviando {data} para o servidor")
        client.sendto(data, addr)
        comand = comand.split(" ")
        if(comand[0] == "GET" and comand.__len__() == 2):
           getFile(comand[1], client , 0)
        elif(comand[0] == "GET" and comand.__len__() == 3):
            getFile(comand[1], client , int(comand[2]))
        else:
            data , addr = client.recvfrom(BUFFER)
            data = decodePackage(data)
            print(data[2].decode("utf-8"))
        

if __name__ == "__main__":
    main()
