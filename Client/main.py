import socket
import struct
import sys

# Acessando os argumentos passados
argumentos = sys.argv


import hashlib

# Função para calcular o checksum dos dados
def calculate_checksum(data):
    checksum = hashlib.md5(data).hexdigest()  # Usando MD5 como exemplo, você pode escolher outro algoritmo
    return checksum




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
            with open(f"client/arquivos/{comand[1]}", "w",encoding='utf-8') as file:
                while True:
                    data, addr = client.recvfrom(1500)
                    if data.decode("utf-8") == "EOF":
                        break
                    print("Recebendo")
                    checksum_length = struct.unpack("!H", data[:2])[0]
                    checksum = data[2:2+checksum_length].decode()
                    print(checksum)
                    data = data[2+checksum_length:]
                    calculated_checksum = calculate_checksum(data)
                    if checksum == calculated_checksum:
                        print("Checksum válido")
                    if data.decode("utf-8") == "Arquivo não encontrado":
                        print ("Arquivo não encontrado")
                        break
                    file.write(data.decode("utf-8"))
            print (f"Server: arquivo {comand[1]} recebido com sucesso")
        else:
            data,addr = client.recvfrom(1024)
            print (data.decode("utf-8"))
            print (addr)
        

if __name__ == "__main__":
    main()
